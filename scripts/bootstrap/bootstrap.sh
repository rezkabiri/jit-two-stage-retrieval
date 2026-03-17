#!/bin/bash
# scripts/bootstrap.sh: Cold-start script for JIT Two-Stage Retrieval RAG

set -e

PROJECT_ID=$1
REGION=${2:-us-central1}
TF_STATE_BUCKET="${PROJECT_ID}-tf-state"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./scripts/bootstrap.sh <PROJECT_ID> [REGION]"
    exit 1
fi

echo "🚀 Bootstrapping project: $PROJECT_ID in $REGION..."

# 1. Enable Critical APIs
echo "Enabling APIs..."
gcloud services enable \
    compute.googleapis.com \
    iam.googleapis.com \
    cloudresourcemanager.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com \
    aiplatform.googleapis.com \
    discoveryengine.googleapis.com \
    iap.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    --project "$PROJECT_ID"

# 2. Create Terraform State Bucket if not exists
if ! gsutil ls -b "gs://${TF_STATE_BUCKET}" >/dev/null 2>&1; then
    echo "Creating GCS bucket for Terraform state: gs://${TF_STATE_BUCKET}"
    gsutil mb -l "$REGION" -p "$PROJECT_ID" "gs://${TF_STATE_BUCKET}"
    gsutil versioning set on "gs://${TF_STATE_BUCKET}"
else
    echo "Terraform state bucket already exists: gs://${TF_STATE_BUCKET}"
fi

echo "✅ Bootstrap complete! You can now run Terraform in infrastructure/environments/"
