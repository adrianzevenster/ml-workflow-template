#!/usr/bin/env bash
set -euo pipefail

# Authenticate with Google Cloud (if running in GCP environment with ADC it works automatically)
# gcloud auth activate-service-account --key-file=/path/to/key.json

# Initialize DVC (if not already initialized)
if [ ! -d ".dvc" ]; then
  dvc init --no-scm
fi

# Pull parameters and optionally any remote cache
# dvc remote add -d localremote /app/.dvc/cache || true
# dvc pull || true

# Run full pipeline
# Stage: set up GCP logging & monitoring
dvc repro setup_logging

# Stage: fetch/process PDFs → Document AI & Gemini
dvc repro run_pipeline

# Stage: post processing & decision
dvc repro post_process

# Stage: quality checks
dvc repro data_quality

# Stage: lint
dvc repro lint

# Show metrics at the end
dvc metrics show ${WORK_DIR}/metrics.json || true

# Keep container alive if needed, otherwise exit
exec "$@"