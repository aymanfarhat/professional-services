#!/bin/bash

# Create a dataprocinit actions file on GCS
cat >init-actions.sh <<EOL
#!/bin/bash
python -m pip install "apache-beam[gcp]==2.31.0"
. /usr/bin/flink-yarn-daemon
EOL

gsutil cp init-actions.sh gs://$GCS_BUCKET/scripts/init-actions.sh
rm init-actions.sh

# Initialize a new dataproc cluster with Flink + Spark + related dependencies
gcloud dataproc clusters create flink-cluster-$RANDOM \
    --region=$GCP_REGION \
    --zone=$GCP_ZONE  \
    --single-node \
    --master-machine-type=n1-standard-4 \
    --master-boot-disk-size=500 \
    --image-version=2.0-debian10 \
    --optional-components=FLINK,DOCKER \
    --project=$GCP_PROJECT \
    --initialization-actions=gs://$GCS_BUCKET/scripts/init-actions.sh
