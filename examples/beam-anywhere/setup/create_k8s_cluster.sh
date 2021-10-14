#!/bin/bash
# Note: Make sure the Kubernetes Engine API is enabled before running this script
# https://cloud.google.com/kubernetes-engine/docs/quickstart
gcloud beta container \
--project "$GCP_PROJECT" clusters create "beam-flink-cluster-$RANDOM" \
--zone "$GCP_ZONE" \
--no-enable-basic-auth \
--cluster-version "1.20.9-gke.1001" \
--release-channel "regular" \
--machine-type "e2-medium" \
--image-type "COS_CONTAINERD" \
--disk-type "pd-standard" \
--disk-size "20" \
--metadata disable-legacy-endpoints=true \
--scopes "https://www.googleapis.com/auth/cloud-platform" \
--max-pods-per-node "110" \
--num-nodes "3" \
--logging=SYSTEM,WORKLOAD \
--monitoring=SYSTEM \
--enable-ip-alias \
--network "projects/$GCP_PROJECT/global/networks/default" \
--subnetwork "projects/$GCP_PROJECT/regions/$GCP_REGION/subnetworks/default" \
--no-enable-intra-node-visibility \
--default-max-pods-per-node "110" \
--no-enable-master-authorized-networks \
--addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
--enable-autoupgrade \
--enable-autorepair \
--max-surge-upgrade 1 \
--max-unavailable-upgrade 0 \
--enable-shielded-nodes \
--node-locations "$GCP_ZONE"
