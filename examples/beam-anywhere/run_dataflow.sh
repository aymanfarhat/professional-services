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
