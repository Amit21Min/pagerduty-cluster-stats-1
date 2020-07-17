# pagerduty_cluster_stats

### Setting up secrets/tokens
Place https://cloud.redhat.com/openshift/token token in a file named "token.txt" in the directory "V3V4_Cluster_Info"
  This token needs to be generated by a user with high enough Org permissions to view all clusters

Place https://support.pagerduty.com/docs/generating-api-keys PD API token in a file named "api_token.txt" in the directory "PD_Incidents"
  This token needs to be generated by a PagerDuty group admin - Possibly Aaron Weitekamp or Bill Montgomery

Generate google sheets API service_account from https://console.developers.google.com/apis/credentials?project=incidents-282615&folder=&organizationId= and place the json in a file "client_secret.json" in the working directory.
You must share the google doc with the email listed under the json key "client_email". This will allow the scripts to have read/write access to the google sheet.

Once you have token.txt, api_token.txt, client_secret.json, and shared the email with the google sheet, the scripts are ready to be run.

### Creating and running the container
Make the image<br/>
`make`<br/>
Create the container<br/>
`docker create quay.io/ammin/pagerduty-cluster-stats`<br/>
Check to see if the container is created & Get the CONTAINER ID<br/>
`docker ps -a`<br/>
start the container<br/>
`docker start <CONTAINER ID><br/>


### Info

Currently does not support the telemeter/sre_ldap page, as the scripts are required to be run on a vpn.

all data is sent to the google sheet found at https://docs.google.com/spreadsheets/d/1ry_tos2ZityB4futWmUTNmXN5q-NnZwIF_BqNv9n8E8/edit#gid=1510693856 - owned by Hemant Wadhwani (@tony) 

all .sh scripts were made by @tony
