import subprocess
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
from time import sleep

print("running run_time.py")

while True:
    subprocess.call(['./run_time.sh'])

    # authorize google sheet api with credentials and import csv to sheets
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("../client_secret.json", scope)
    client = gspread.authorize(creds)

    # V4 Cluster worksheet
    baseSheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8')
    
    with open('run_time.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile, delimiter=";"))
    try:
        sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("run_time")
        baseSheet.del_worksheet(sheet)
    except:
        pass

    baseSheet.add_worksheet("run_time",1,1)
    sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("run_time")
    try:
        sheet.insert_rows(data, row=1)
    except:
        pass
        print("error most likely due to too many read/writes in timeframe")


    print("sre_ldap: sleeping for 6 hours")
    sleep (60) # -10 minutes in an effort to spread out read/writes on the google sheets api
