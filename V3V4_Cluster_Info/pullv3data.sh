#!/bin/sh
echo "id, name,  external_id,  state,  openshift_version,  creation_timestamp,  activity_timestamp, master_count, infra_count, compute_count, vcpu_max, memory_max, cloud_provider, region_name, managed, user_count, project_count, pod_count" >V3_Cluster_Info.csv 
echo "cluster_id, type, deleted, created_at, updated_at, memory_max, machine_type.name">V3_Node_Info.csv

for CLUSTER_ID in $(curl -q https://dedicated.openshift.com/api/clusters/summary\?authorization_username=ammin.openshift -H 'Authorization: Bearer 43f4d392f879c98ab84abe313f0d95da' | jq -r '.[] | select(.status == "provisioned") | .id')
do
curl -q https://dedicated.openshift.com/api/clusters/$CLUSTER_ID/detail\?authorization_username=ammin.openshift -H 'Authorization: Bearer 43f4d392f879c98ab84abe313f0d95da' | jq > tempfilev3osd
cat tempfilev3osd | jq -c -r "[.id, .name, .display_name, .status, .version, .created_at, .updated_at, .master_count, .infra_count, .compute_count, .vcpu_max, .memory_max, .cloud.name, .region.name, .deployment, .user_count, .project_count, .pod_count]"  >> V3_Cluster_Info.csv
cat tempfilev3osd | jq '.nodes[]' | jq -c ['.cluster_id, .type, .deleted, .created_at, .updated_at, .memory_max, .machine_type.name'] >> V3_Node_Info.csv
done
perl -pi -e 's/\[//g' V3_Cluster_Info.csv
perl -pi -e 's/\]//g' V3_Cluster_Info.csv
perl -pi -e 's/\[//g' V3_Node_Info.csv
perl -pi -e 's/\]//g' V3_Node_Info.csv
