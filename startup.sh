#!/bin/sh

pkill -9 -f telemeter.py
pkill -9 -f getIncidents.py
pkill -9 -f pullv3v4.py

cd PD_Incidents/
python ./getIncidents.py &
cd ../Telemeter_Data
python telemeter.py &
cd ../V3V4_Cluster_Info
python ./pullv3v4.py &