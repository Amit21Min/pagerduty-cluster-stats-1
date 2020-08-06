#!/bin/bash
echo "cn:;rhatJobTitle:;rhatOfficeLocation:;co:;employeeType:;rhatGeo:;hatCostCenterDesc:;rhatCostCenter:;rhatLocation:;mail;l:;creation_timestamp;manager:">full_list.csv
for i in `ls RH_*`
do
CN=`grep "cn:" $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
RHATJOBTITLE=`grep "rhatJobTitle:" $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
RHATOFFICELOCATION=`grep "rhatOfficeLocation:" $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
CO=`grep "co:" $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
EMPLOYEETYPE=`grep "employeeType:" $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
RHATGEO=`grep "rhatGeo:" $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
RHATCOSTCENTERDESC=`grep "rhatCostCenterDesc:" $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
RHATCOSTCENTER=`grep "rhatCostCenter:" $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
RHATLOCATION=`grep "rhatLocation:" $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
L=`grep '^l:' $i|cut -d':' -f2,3,4,5,6,7,8,9,10,11`
MAIL=`grep "mail:" $i`
TEMPDOH=`cat $i | grep "rhatHireDate:" | cut -d' ' -f2`
DOHYYYY=`echo ${TEMPDOH:0:4}`
DOHMM=`echo ${TEMPDOH:4:2}`
DOHDD=`echo ${TEMPDOH:6:2}`
DOH=`echo "$DOHYYYY-$DOHMM-$DOHDD"`
MANAGER=`cat $i| grep 'manager: uid=' |cut -d'=' -f2 | cut -d',' -f1`
echo "$CN;$RHATJOBTITLE;$RHATOFFICELOCATION;$CO;$EMPLOYEETYPE;$RHATGEO;$RHATCOSTCENTERDESC;$RHATCOSTCENTER;$RHATLOCATION;$MAIL;$L;$DOH;$MANAGER" >> full_list.csv
done
rm RH_*
