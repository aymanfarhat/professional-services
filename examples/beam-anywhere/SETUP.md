# Setup

## Initialize a GCS bucket

This bucket serves as a sink to the multiple outputs related to the multiple runs of the pipeline under different runners

`gsutil mb [YOUR-BUCKET-NAME]`

## Environment variables 
The following environment variables are expected to be present wherever the scripts in this repo will be triggered from

```
export GOOGLE_APPLICATION_CREDENTIALS="YOUR_CREDENTIALS.json" # Set if running on local machine
export GCP_PROJECT="YOUR_PROJECT_ID"
export GCS_BUCKET="YOUR_BUCKET_NAME"
export GCP_LOCATION="YOUR_GCP_PROJECT_ZONE" 
```
 
## Setting up the services / runners

### Hadoop cluster supporting Flink and Spark via DataProc
- Initialize the cluster via executing the script `./setup/create_dataproc_cluster.sh`

### K8S cluster supporting Flink via GKE
- Initialize a k8s cluster on your system. Or for testing purposes via GKE by executing `./setup/create_k8s_cluster.sh`
- Setup Flink on your k8s cluster, we recommend installing the [flink-on-k8s-operator](https://github.com/GoogleCloudPlatform/flink-on-k8s-operator) which includes a step by step guide. Alernatively, if you're doing the setup on GKE, you could deploy it directly from the GKE marketplace under Application, with one click install.
- After a Flink operator is setup on the K8s cluster, you should be ale to submit new jobs either via client pod on the same cluster or vi
- Once the operator is setup, you should be able to submit Beam Flink jobs easily through a client pod in the same cluster or via kubectl
- Any code that runs on the cluster, will need to be built as part of a container image pushed to a registry, we've included in this demo a sample Dockerfile for building up the container image, we're using gcr.io as an example registry
- Make sure to connect kubectl to the GKE cluster where the Flink jobs will be submitted to

