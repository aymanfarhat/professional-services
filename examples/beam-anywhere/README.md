# Beam Anywhere

In this example, we demonstrate the compatibility of running Apache Beam batch jobs across multiple runners and in different environments for the same Beam pipeline code with no modifications. This helps in demonstrating the reversibility of Beam pipelines written for running on Dataflow to other setups running  supported Beam runners.

The demo is made to run on GCP based services representing:
-  GCP Dataflow
- A hadoop cluster (via DataProc) supporting Spark and Flink
- Kubernetes cluster (via GKE) supporting Flink via the [Flink K8s operator](https://github.com/GoogleCloudPlatform/flink-on-k8s-operator)

![Alt text](/repo-assets/diagram.png?raw=true "Diagram")

## About the demo

The pipeline code for this demo is currently based on a simplified WordCount example utilizing several popular features of a typical beam batch pipeline such as Map, FlatMap, CombinePerKey and IO operations. The pipeline takes a text file as input and outputs a text file containing key/value pairs representing the count for each word. The final step, would be to verify that the output results are indeed the same, for that we've added a simple utility script for diffing output k/v text output file values against each other.

Note: Following the setup and running guide of this demo, it should be easy enough to replace or modify this pipeline to test other features across the different runners. 

## Setting up runners / environments
For each target environment, [this guide](SETUP.md) summarizes how to set that up relying on the relative GCP service.

## Running the pipeline Beam pipeline
In the running guide below, we demonstrate how to run the example beam code in the different environments / runners, finally we illustrate a simple way for comparing output results.

### Via DataFlow
- Run the job via
    ```
    python ./src/word_count.py \
     --input="gs://dataflow-samples/shakespeare/kinglear.txt" \
     --output="gs://$GCS_BUCKET/output-dataflow/" \
     --temp_location="gs://$GCS_BUCKET/tmp" \
     --staging_location="gs://$GCS_BUCKET/staging" \
     --region=$GCP_REGION \
     --project=$GCP_PROJECT \
     --runner="DataflowRunner" \
     --job_name="dataflow-job" \
     --shards=1
    ```
- Results should show up in the `output-dataflow` folder in the bucket

### Via Flink runner in a Hadoop cluster
- SSH into the master node
- Upload `word_count.py` and set the same env
- Run the job
  ```
  python ./src/word_count.py \
      --input="gs://dataflow-samples/shakespeare/kinglear.txt" \
      --output="gs://$GCS_BUCKET/output-flink/" \
      --temp_location="gs://$GCS_BUCKET/tmp/" \
      --staging_location="gs://$GCS_BUCKET/staging/" \
      --region=$GCP_LOCATION \
      --project=$GCP_PROJECT \
      --runner="FlinkRunner" \
      --job_name="flink-job" \
      --shards=1
  ```
- Results should show up in the `output-flink` folder in the bucket
- *Note:* Shards is an optional parameter used to later ease the diffing of results given that different runners might create different number of shards. Using in production might affect performance.

### Via Spark runner in a Hadoop cluster
- This would follow the same process as above with no modification to the code as well, just a small change on the execution script by changing the runner to `SparkRunner` as follows
  ```
  python ./src/word_count.py \
      --input="gs://dataflow-samples/shakespeare/kinglear.txt" \
      --output="gs://$GCS_BUCKET/output-spark/" \
      --temp_location="gs://$GCS_BUCKET/tmp/" \
      --staging_location="gs://$GCS_BUCKET/staging/" \
      --region=$GCP_LOCATION \
      --project=$GCP_PROJECT \
      --runner="SparkRunner" \
      --job_name="spark-job" \
      --shards=1
  ```
- Results should show up in the `output-spark` folder in the bucket

### Via Flink on a Kubernetes cluster
After setting up the K8S cluster with the Flink operator and related pods, you can submit Beam Flink jobs against a deployed docker images of the pipeline code, in this example deployed to Google Container Registry. The job is submitted via a kubectl client configured against the cluster.

```
cat <<EOF | kubectl apply --filename -
apiVersion: batch/v1
kind: Job
metadata:
  name: flink-job-py-2
  namespace: flink-ns
spec:
  template:
    metadata:
      labels:
        app: flink-operator-demo
    spec:
      containers:
        - name: beam-wordcount-py
          image: "gcr.io/$GCP_PROJECT/beamwc"
          command: ["python3", "./src/word_count.py"]
          args:
            - "--runner=FlinkRunner"
            - "--flink_master=$FLINK_CLUSTER_JOB_MANAGER:8081"
            - "--flink_submit_uber_jar"
            - "--environment_type=EXTERNAL"
            - "--environment_config=localhost:50000"
            - "--input"
            - "gs://dataflow-samples/shakespeare/kinglear.txt"
            - "--output"
            - "gs://$GCP_BUCKET/output-flink-k8s/"
      restartPolicy: Never
EOF
```

### Comparing results
We've included in the code a simple python script for diffing both output files using symmetric difference in order to verify that results are identical. An empty set in the result means both kv sets are identical. Can be ran as the example below:

```
python diff.py \
    --file1="gs://demo-beam-runners-323508/output-flink/-00000-of-00001" \
    --file2="gs://demo-beam-runners-323508/output-dataflow/-00000-of-00001"
```

## Disclaimer
This is not an officially supported Google product. This code is written for the purpose of demo only.
