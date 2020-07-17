rm LDAP_DATA
for i in `cat manager_list`; do ldapsearch -LLL  -x -b ou=users,dc=redhat,dc=com -h ldap.corp.redhat.com manager=uid=$i,ou=users,dc=redhat,dc=com >> LDAP_DATA; done
