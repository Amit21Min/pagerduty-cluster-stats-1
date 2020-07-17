from prometheus_api_client import Metric, MetricsList, PrometheusConnect
from prometheus_api_client.utils import parse_datetime, parse_timedelta
from time import mktime, strptime, strftime, sleep
from datetime import datetime, timedelta, date
import re

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("../client_secret.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("telemeter")

url = "https://telemeter-lts.datahub.redhat.com"
token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkaC1wcm9kLXRlbGVtZXRyeSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJvcGVuc2hpZnQtc3JlLXRlbGVtZXRlci1yZXBvcnRlci10b2tlbi14ZHA5eCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJvcGVuc2hpZnQtc3JlLXRlbGVtZXRlci1yZXBvcnRlciIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjliN2I5N2U4LTFhYmEtMTFlYS05NjJmLWZhMTYzZTUwOGMxNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkaC1wcm9kLXRlbGVtZXRyeTpvcGVuc2hpZnQtc3JlLXRlbGVtZXRlci1yZXBvcnRlciJ9.dsN5Cda11tfTzPKUjtHfix_hfK3lSbWdtqDUFmlTDq-Jf9kP8TZfwmio5aCIPcDHgz_W7Kee0uU_asRIZrla3ISbBxKhj4KsaoU2H9ZidKctOmOCr6zhl-4WXsQcpexayLpkR8LdcE74XB-g74nDJErXiuBQjhsvQRnDB6FT1OpqLB9nu3NomaOQ2zTpDkWK13TLB5ifNy9GXt47HFY89llNZfJQxSSQ3h7w2uzOlGDoCQjn1FBN2OYEQ75Vj-0atY4k9-mpv4DWusEJG2au-t7CfKmpooUQVOAW3EkG8kyYghDFHwL2ZofDHZC_06MUUTVC9ozGu6b55TWerpVE4g"

pc = PrometheusConnect(url=url, headers={"Authorization": "bearer {}".format(token)}, disable_ssl=False)

# gets query information for a specific date - each function call is a customized query
def getClusterMetric(buildRow, time):
    data = None
    try:
        data = pc.custom_query(query='count(sum by (_id)(subscription_labels{managed="true"}) * 1)', params={"time":time.strftime('%Y-%m-%dT%H:%M:%SZ')})      
        for arr in data:
            buildRow.append(arr.get('value')[1])
    except:
        pass

def getCPUCores(buildRow, time):
    data = None
    try:
        data = pc.custom_query(query='sum(sum by (_id)(cluster:capacity_cpu_cores:sum) + \
            on(_id) group_left(managed)(sum by (_id)(subscription_labels{managed="true"}) * 0))', params={"time":time.strftime('%Y-%m-%dT%H:%M:%SZ')})
        for arr in data:
            buildRow.append(arr.get('value')[1])
    except:
        pass

def getNodeInstance(buildRow, time):
    data = None
    try:
        data = pc.custom_query(query='sum(sum by (_id)(cluster:node_instance_type_count:sum) + \
            on (_id) group_left(managed)(sum by (_id)(subscription_labels{managed="true"})* 0))', params={"time":time.strftime('%Y-%m-%dT%H:%M:%SZ')})
        for arr in data:
            buildRow.append(arr.get('value')[1])
    except:
        pass


def main():
    while True:
        start = ''
        try:
            row = sheet.row_values(2)
            regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:){2}[0-9]{2}Z'
            for value in row:
                if re.search(regex, value):
                    start = re.search(regex, value)[0]
                    break
        except:
            pass
        # if start is an empty string, then it didn't find a last recorded date scrape, so start from 2020-01-01 (should only happen on an empty worksheet)
        if not start:
            start = datetime.fromtimestamp(mktime(strptime('2020-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')))
        # if start isn't an empty string, convert it to a datetime object so we have an initial scrape date
        else:
            start = datetime.fromtimestamp(mktime(strptime(start, '%Y-%m-%dT%H:%M:%SZ')))
        # take the most recently scraped date and go to the next day
        scrapeTime = start + timedelta(days=1)
        
        # make sure that it isn't trying to query a date in the future. If it is, just sleep for 12 hours and try again.
        now = datetime.now()
        while scrapeTime > now:
            print('telemeter: sleeping for 100 mins: up to date')
            sleep(60 * 100)
            now = datetime.now()
        print("getting metric at: " + scrapeTime.strftime('%Y-%m-%dT%H:%M:%SZ'))

        buildRow = [] # for aggregating the data in 1 array for google sheet importing
        adjustTime = 0
        slept = 0
        #check to make sure there are entries for each metric - if buildRow is not filled with 4 separate values, then re-do the search with +60 minute intervals until we get values
        while len(buildRow) < 4:
            now = datetime.now()
            # check to make sure that the script isn't checking a future date (again in the loop as a precaution)
            while scrapeTime > now:
                print('sleeping for 1 hour: up to date')
                sleep(3600)
                now = datetime.now()
            
        
            print("TRYING TO GET ALL METRICS at " + scrapeTime.strftime('%Y-%m-%dT%H:%M:%SZ'))
            buildRow = [scrapeTime.strftime('%Y-%m-%dT%H:%M:%SZ')]

            #custom query to gather - # of clusters
            getClusterMetric(buildRow, scrapeTime + timedelta(minutes=adjustTime))
            # CAPACITY_CPU_CORES
            getCPUCores(buildRow, scrapeTime + timedelta(minutes=adjustTime))
            # NODE_INSTANCE_TYPE_COUNT
            getNodeInstance(buildRow, scrapeTime + timedelta(minutes=adjustTime))

            adjustTime = adjustTime + 60
            # if we've adjusted the time by over 24 hours, let's sleep for 1 hour and try again. if it happens for 15 consecutive hours, then maybe there is somehow no data. Skip to the next day.
            if slept == 15:
                adjustTime = 0
                slept = 0
                scrapeTime = scrapeTime + timedelta(days=1)
                print("skipping a day")
            if adjustTime >= 1440:
                print("telemeter: sleeping for 1 hour due to no response")
                sleep(3600)
                slept = slept + 1

            print(buildRow)
        # once buildRow has 4 values in it, we can append it to the google sheet
        sheet.insert_row(buildRow, index=2)

if __name__ == "__main__":
    main()