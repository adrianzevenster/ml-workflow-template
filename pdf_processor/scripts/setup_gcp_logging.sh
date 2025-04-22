#!/usr/bin/env bash
set -euo pipefail

# Args:
#   $1 = PROJECT_ID
#   $2 = LOCATION
#   $3 = DOCAI_PROCESSOR_ID
#   $4 = ENDPOINT_ID
#   $5 = LOGS_DATASET
#   $6 = DOCAI_SINK_NAME
#   $7 = VERTEX_SINK_NAME
#   $8 = MONITORING_JOB_NAME
#   $9 = LOG_SAMPLING_PCT
#  $10 = DRIFT_THRESHOLD
#  $11 = MONITOR_INTERVAL_HOURS

PROJECT_ID=$1
LOCATION=$2
DOCAI_PROC_ID=$3
ENDPOINT_ID=$4
DATASET=$5
DOCAI_SINK=$6
VERTEX_SINK=$7
JOB_NAME=$8
SAMPLE_PCT=$9
DRIFT_THR=${10}
INTERVAL_H=${11}

# 1. Create BigQuery dataset if absent
bq --location=${LOCATION} mk -d --description "Log tables" ${PROJECT_ID}:${DATASET} || true

# 2. Create Logging→BQ sinks (ignore if already exist)
gcloud logging sinks create ${DOCAI_SINK} \
  bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/${DATASET} \
  --log-filter='resource.type="documentai.googleapis.com/DocumentProcessorService"' \
  --project=${PROJECT_ID} || true

gcloud logging sinks create ${VERTEX_SINK} \
  bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/${DATASET} \
  --log-filter='resource.type="aiplatform.googleapis.com/PredictionEndpoint"' \
  --project=${PROJECT_ID} || true

# 3. Grant sink identities write access on the BQ dataset
for SINK in ${DOCAI_SINK} ${VERTEX_SINK}; do
  SA=$(gcloud logging sinks describe ${SINK} --project=${PROJECT_ID} --format="value(writerIdentity)")
  bq update --dataset ${PROJECT_ID}:${DATASET} --add_iam_member=${SA}
done

# 4. Enable logging on your deployed endpoint
gcloud ai endpoints deploy-model ${ENDPOINT_ID} \
  --model=${ENDPOINT_ID} \
  --region=${LOCATION} \
  --enable-logging \
  --logging-sampling-percentage=${SAMPLE_PCT} \
  --machine-type=n1-standard-4 \
  --project=${PROJECT_ID}

# 5. Create a Model Monitoring job for drift detection
gcloud ai model-monitoring-jobs create \
  --project=${PROJECT_ID} \
  --region=${LOCATION} \
  --display-name=${JOB_NAME} \
  --endpoint=${ENDPOINT_ID} \
  --monitor-interval=hour=${INTERVAL_H} \
  --logging-sampling-strategy=random-sample-config=sample-rate=${SAMPLE_PCT} \
  --objective-config=predict-drift-detection-threshold=${DRIFT_THR}

echo "✅ Logging sinks and monitoring job '${JOB_NAME}' are set up."
