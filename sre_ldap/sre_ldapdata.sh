#!/bin/bash
## Script to pull SREP Managers Data from LDAP
echo "Validate the Managers List is correct for the SRE group"
cat manager_list
#echo "Press Enter if OK else press Ctrl + C and update manager list"
#read x 

/usr/bin/sh ldap_command.sh
/usr/bin/sh split.sh LDAP_DATA
/usr/bin/sh create_csv_input_fields.bash

echo "The CSV file full_list.csv  is now ready. The delimiter used is ;"

