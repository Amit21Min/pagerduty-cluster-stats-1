import subprocess
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
from time import sleep

print("running sre_ldap.py")

while True:
    subprocess.call(['./sre_ldapdata.sh'])

    # authorize google sheet api with credentials and import csv to sheets
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("../client_secret.json", scope)
    client = gspread.authorize(creds)

    # V4 Cluster worksheet
    baseSheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8')
    
    with open('full_list.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile, delimiter=";"))

    # Following logic: If data was found: delete the current sheet, create a new sheet, store the data
        
    # 1 subarray is 1 row for the google sheet. If there are less than 10 arrays, then it did not pull >10 users from the sre_ldap script
    if len(data) > 10:
        sheet = baseSheet.worksheet("sre_ldap")
        baseSheet.del_worksheet(sheet)
    else:
        print("sufficient sre_ldap data was not found. Most likely fix: run on red hat vpn. Sleeping for 1 hour")
        sleep(3600)
        continue

    baseSheet.add_worksheet("sre_ldap",1,1)
    sheet = baseSheet.worksheet("sre_ldap")
    try:
        sheet.insert_rows(data, row=1)
    except:
        print("error most likely due to too many read/writes in timeframe")
        pass


    print("sre_ldap: sleeping for 6 hours")
    sleep(3600 * 6 - 10) # -10 minutes in an effort to spread out read/writes on the google sheets api