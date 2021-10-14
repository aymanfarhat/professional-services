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
