from pdpyras import APISession
import re
import time
import math
import json
import csv
import datetime
from datetime import datetime, timedelta
from time import mktime, strptime, strftime, sleep

import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("../client_secret.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("PD Incidents")

api_token = '7sPx5PBdFfG3QeFQ5_NQ'
session = APISession(api_token)

# clean up any whitespace in sheet- this is just in case the script crashes/fails as it tries to insert rows, as there will be many empty rows
def cleanWhitespace():
    records = sheet.get_all_records()
    # check if there are empty rows. If there are 3 empty rows, we will delete from 2 --> 2 + (3-1). This is deleting rows 2-4.
    x = 2 #row index marker
    for row in records:
        if row.get("incident_ID"):
            break
        x += 1
    # if the row index marker has changed from the inital row 2, then delte rows 2 --> x-1
    if x != 2:
        sheet.delete_rows(2, x-1)
    return

def getScrapeStart():
        scrapeSince = ""
        #get the trigger time of the last incident recorded - Start scraping 24 hours before this time to ensure that we don't miss any resolved incidents
        try:
            incident = sheet.row_values(2)
            scrapeSince = ''
            regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:){2}[0-9]{2}Z'
            for value in incident:
                if re.search(regex, value):
                    scrapeSince = re.search(regex, value)[0]
                    break
        except:
            pass
        
        if not scrapeSince:
            scrapeSince = "2020-04-01T00:00:00Z"

        # Now subtract 3 days from the scrapeSince - this makes sure that we grab any incidents that took a long time to resolve - This misses incidents that are >3 days to resolve, but they aren't relevant - mostly "cluster missing for 20 days" etc
        convertScrape = time.strptime(scrapeSince, '%Y-%m-%dT%H:%M:%SZ')
        convertSeconds = time.mktime(convertScrape)
        convertSeconds = convertSeconds - (86400 * 3) # 86400 seconds in a day - 3 days
        scrapeSince = str(datetime.fromtimestamp(convertSeconds).isoformat()) + "Z"
        print("Scrape since " + scrapeSince)
        return scrapeSince

def insertRows(incidents):
    # converts the incident dict into an array of arrays, with 1 array being a row. Then all the rows can be bulk inserted
    buildRows = []
    for key in incidents:
        buildRow = [key]
        for value in incidents[key]:
            buildRow.append(incidents[key][value])
        buildRows.insert(0,buildRow)

    # bulk insert the rows (array --> row)
    sheet.insert_rows(buildRows, row=2)

def main():
    while True:
        cleanWhitespace()
        scrapeSince = getScrapeStart()

        incidents = {} # for aggregating all of the incident data that we will insert into the google sheet
        incidentDict = {} # for retrieving the current incidents listed in the google sheet - resolved incidents are checked against these keys to make sure incidents aren't inserted more than once
        try:
            incidentIDs = sheet.batch_get(['A2:A5002'])
            for incident in incidentIDs[0]:
                incidentDict.update({incident[0] : incident[0]})
        except:
            pass

        for incident in session.iter_all('incidents', params={'since': scrapeSince}):
            # check if resolved status and it isn't in the last 5000 google spreadsheet rows
            if incident.get("status") == "resolved" and str(incident.get("incident_number")) not in incidentDict:
                # calculate the time to resolve
                triggerTime = incident.get("created_at")
                resolveTime = incident.get("last_status_change_at")
                triggerTime = time.strptime(triggerTime, '%Y-%m-%dT%H:%M:%SZ')
                resolveTime = time.strptime(resolveTime, '%Y-%m-%dT%H:%M:%SZ')
                TTR = time.mktime(resolveTime) - time.mktime(triggerTime)
                    
                # clusterName, incidentName, and incidentID variables
                clusterName = incident.get("service").get("summary")
                incidentName = incident.get("title")
                incidentID = incident.get("incident_number")

                # alertName and severity - have to hit a different API endpoint to fetch the original Alert - this is what slows down the script by a lot.
                alertDetails = ""
                try:
                    alert = session.rget(incident.get("first_trigger_log_entry").get("self"), params={'include[]':'channels'})
                    alertDetails = alert.get("channel").get("details").get("firing")
                except:
                    pass
                
                alertName = ""
                alertSeverity = ""
                try:
                    alertName = re.search('(?<=alertname = )(.*)', alertDetails)[0]
                    alertSeverity = re.search('(?<=severity = )(.*)', alertDetails)[0]
                except:
                    alertName = incidentName
                    alertSeverity = "critical"

                # time of incident resolve variable
                resolveTime = incident.get("last_status_change_at")

                # get "noisy" - If an employee was notified and the incident resolved before they acknowledged, it is objectively noisy
                incidentID = incident.get("html_url").split("/incidents/")[1]
                log_entries = session.rget(f"/incidents/{incidentID}/log_entries")

                alerted = False
                acknowledged = False
                noisy = False
                acknowledged_by = ""
                # Noting if incident has log entries for specific types - tells us if an SRE was alerted/ SRE acknowledged alert
                for key in log_entries:
                    if (key["type"] == "notify_log_entry"):
                        alerted = True
                    if (key["type"] == "acknowledge_log_entry"):
                        acknowledged = True
                    try:
                        acknowledged_by = key["summary"].split("Acknowledged by ")[1] # gets SRE name
                    except:
                        pass
                if (alerted and not acknowledged):
                    noisy = True

                # get the trigger time variable
                triggerTime = incident.get("created_at")
                # re-get the incident ID in number format
                incidentID = incident.get("incident_number")
                # get the escalation policy
                policy = incident.get("escalation_policy").get("summary")

                incidentInfo = {
                    "incidentname": incidentName,
                    "clustername": clusterName,
                    "triggered": triggerTime,
                    "resolved": resolveTime,
                    "ttr_seconds": TTR,
                    "alerted": alerted,
                    "acknowledged": acknowledged,
                    "noisy": noisy,
                    "escalation_policy": policy,
                    "acknowledged_by": acknowledged_by,
                    "alertname": alertName,
                    "severity": alertSeverity
                }

                incidents.update( {incidentID : incidentInfo})

                # Gathering takes a while, so if we've gathered 1000, put it in the google sheet - in case the script hits an error.
                if (len(incidents)) > 1000:
                    break
        
        insertRows(incidents)

        # If the google sheet is relatively up to date, sleep for an hour until scraping again. If it's nowhere near up to date, don't sleep and keep scraping.
        # This is useful for scraping without sleeping when the sheet is extremely outdated.
        scrapeSince = datetime.fromtimestamp(mktime(strptime(scrapeSince, '%Y-%m-%dT%H:%M:%SZ'))) + timedelta(days=3)
        print(scrapeSince)
        if scrapeSince > datetime.now():
            print('PD_Incidents: sleeping for 1 hour')
            time.sleep(3600)


if __name__ == "__main__":
    main()
