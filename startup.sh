#!/bin/sh

pkill -9 -f telemeter.py
pkill -9 -f getIncidents.py
pkill -9 -f pullv3v4.py
pkill -9 -f ldap.py
pkill -9 -f run_time.py

cd PD_Incidents/
python3 ./getIncidents.py &
cd ../Telemeter_Data
python3 telemeter.py &
cd ../V3V4_Cluster_Info
python3 ./pullv3v4.py &
cd ../run_time
python3 run_time.py
cd ../sre_ldap
python3 ldap.py
