import subprocess
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
from time import sleep

print('Place your ocm login token in "token.txt" - found at https://cloud.redhat.com/openshift/token')
# Logging into ocm with token and running the 2 bash scripts to generate csv data
login = 'ocm login --token="'
with open('token.txt', 'r') as f:
    login = login + f.read() + '"'

while True:
    subprocess.run(login, shell=True)
    subprocess.call(['./pullv4data.sh'])
    subprocess.call(['./pullv3data.sh'])

    # authorize google sheet api with credentials and import csv to sheets
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("../client_secret.json", scope)
    client = gspread.authorize(creds)


    sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("V4Cluster")
    with open('ocm_ocp4.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile))
    sheet.clear()
    sheet.insert_rows(data, row=1)

    sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("V3Cluster")
    with open('V3_Cluster_Info.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile))
    sheet.clear()
    sheet.insert_rows(data, row=1)

    sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("V3Nodes")
    with open('V3_Node_Info.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile))
    sheet.clear()
    sheet.insert_rows(data, row=1)

    print("v3v4: sleeping for 1 hour")
    sleep(3600)
    break