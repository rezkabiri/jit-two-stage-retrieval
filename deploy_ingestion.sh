#!/bin/bash
# deploy_ingestion.sh: Script to deploy the RAG Ingestion Cloud Function
# This script uses standard gcloud commands and REST APIs to bypass permission issues.

set -e

# --- CONFIGURATION ---
PROJECT_ID="jit-tsr-rag-prod"
REGION="us-central1"
ENV="prod" 
DATA_STORE_ID="rag-docs-${ENV}-v6"
# ---------------------

PROJECT_ID=$(echo "$PROJECT_ID" | xargs)

if [[ "$PROJECT_ID" == "REPLACE_WITH_PROJECT_ID" ]]; then
    echo "❌ ERROR: Please update PROJECT_ID in the script before running."
    exit 1
fi

echo "🚀 Starting deployment for project: $PROJECT_ID ($ENV)..."

# 0. Fetch Project Details
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
BUCKET_NAME="${PROJECT_ID}-${ENV}-ingestion"
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# 1. Enable APIs (Standard)
echo "Enabling necessary APIs..."
gcloud services enable \
    cloudfunctions.googleapis.com \
    eventarc.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    pubsub.googleapis.com \
    storage.googleapis.com \
    --project "$PROJECT_ID"

# 2. Grant Core IAM Permissions
echo "Setting up IAM permissions..."

# A. Storage to Pub/Sub
echo "Configuring Storage to Pub/Sub..."
STORAGE_SA=$(gcloud storage service-agent --project="$PROJECT_ID")
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$STORAGE_SA" \
    --role="roles/pubsub.publisher"

# B. Force create Eventarc Service Identity via REST API (bypass local gcloud beta issue)
echo "Ensuring Eventarc Service Identity exists..."
TOKEN=$(gcloud auth print-access-token)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d "{}" \
     "https://serviceusage.googleapis.com/v1/projects/$PROJECT_NUMBER/services/eventarc.googleapis.com:generateServiceIdentity"

echo "Waiting 45s for service identity to propagate..."
sleep 45

EVENTARC_SA="service-$PROJECT_NUMBER@gcp-sa-eventarc.iam.gserviceaccount.com"

# Grant Eventarc SA permission to validate the bucket (Fixes the 403 error)
echo "Granting Eventarc SA storage permissions..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$EVENTARC_SA" \
    --role="roles/eventarc.serviceAgent"

# C. Build & Runtime Permissions
echo "Configuring Build/Runtime permissions..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/eventarc.eventReceiver"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/logging.logWriter"

gcloud iam service-accounts add-iam-policy-binding "$COMPUTE_SA" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/iam.serviceAccountUser" \
    --project="$PROJECT_ID"

# 3. Deploy the Function
echo "Deploying Cloud Function: rag-ingestion..."
gcloud functions deploy rag-ingestion \
    --gen2 \
    --runtime=python311 \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --source=./data-pipeline/ingestion \
    --entry-point=process_gcs_upload \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=$BUCKET_NAME" \
    --set-env-vars GOOGLE_CLOUD_PROJECT="$PROJECT_ID",DATA_STORE_ID="$DATA_STORE_ID"

echo "✅ Deployment complete for $PROJECT_ID!"
