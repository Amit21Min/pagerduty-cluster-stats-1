#!/bin/sh
ocm cluster list --managed --columns  id,name,external_id,state,openshift_version,creation_timestamp,activity_timestamp,nodes.master,nodes.infra,nodes.compute,metrics.cpu.total.value,metrics.memory.total.value,cloud_provider.id,region.id,managed,product.id,multi_az,byoc,cluster_admin_enabled,nodes.total |  awk '{print $1","$2","$3","$4","$5","$6","$7","$8","$9","$10","$11","$12","$13","$14","$15","$16","$17","$18","$19","$20","$21}' > /tmp/ocm_osd.csv

echo "id, name, external_id, state, openshift_version,creation_timestamp, activity_timestamp, master_count, infra_count, compute_count, vcpu_max, memory_max, cloud_provider, region_name, managed, product_id, multi_az, byoc, cluster_admin_enabled, total_nodes" > ocm_ocp4.csv
sed -i '1d' /tmp/ocm_osd.csv 
cat /tmp/ocm_osd.csv >>ocm_ocp4.csv 

