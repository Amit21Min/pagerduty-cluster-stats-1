import subprocess
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
from time import sleep

print('Place your ocm login token in "token.txt" - found at https://cloud.redhat.com/openshift/token')
# build the ocm CLI login command
login = 'ocm login --token '
with open('token.txt', 'r') as f:
    login = login + f.read()


while True:
    # Login to ocm with token.txt and run the bash scripts to generate csv's.
    subprocess.run(login, shell=True)
    # subprocess.call(['./pullv4data.sh'])
    # subprocess.call(['./pullv3data.sh'])

    # authorize google sheet api with credentials and import csv to sheets
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("../client_secret.json", scope)
    client = gspread.authorize(creds)

    # V4 Cluster worksheet
    baseSheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8')
    
    with open('ocm_ocp4.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile))
    try:
        sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("V4Cluster")
        baseSheet.del_worksheet(sheet)
    except:
        pass
    baseSheet.add_worksheet("V4Cluster",1,1)
    sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("V4Cluster")
    sheet.insert_rows(data, row=1)


    # V3 Cluster worksheet
    baseSheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8')
    with open('V3_Cluster_Info.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile))
    try:
        sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("V3Cluster")
        baseSheet.del_worksheet(sheet)
    except:
        pass
    baseSheet.add_worksheet("V3Cluster",1,1)
    sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("V3Cluster")
    sheet.insert_rows(data, row=1)


    # V3 Nodes worksheet
    baseSheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8')
    with open('V3_Node_Info.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile))
    try:
        sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("V3Nodes")
        baseSheet.del_worksheet(sheet)
    except:
        pass
    baseSheet.add_worksheet("V3Nodes",1,1)
    sheet = client.open_by_key('1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8').worksheet("V3Nodes")
    sheet.insert_rows(data, row=1)

    print("v3v4: sleeping for 1 hour")
    sleep(3600)