#!/bin/bash
# scripts/bootstrap/manual_deploy_ingestion.sh: Script to manually deploy the RAG Ingestion Cloud Function
# This script uses standard gcloud commands and REST APIs to bypass permission issues.
# Use this as a "break glass" alternative if Terraform is failing.

set -e

PROJECT_ID=$1
ENV=$2 # stage or prod
DATA_STORE_ID=$3
REGION=${4:-us-central1}

if [[ -z "$PROJECT_ID" || -z "$ENV" || -z "$DATA_STORE_ID" ]]; then
    echo "❌ ERROR: Missing arguments."
    echo "Usage: $0 <PROJECT_ID> <ENV> <DATA_STORE_ID> [REGION]"
    exit 1
fi

echo "🚀 Starting manual deployment for project: $PROJECT_ID ($ENV)..."

# 0. Fetch Project Details
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
BUCKET_NAME="${PROJECT_ID}-${ENV}-ingestion"
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# 1. Enable APIs
echo "Enabling necessary APIs..."
gcloud services enable 
    cloudfunctions.googleapis.com 
    eventarc.googleapis.com 
    run.googleapis.com 
    artifactregistry.googleapis.com 
    pubsub.googleapis.com 
    storage.googleapis.com 
    --project "$PROJECT_ID"

# 2. Grant Core IAM Permissions
echo "Setting up IAM permissions..."

# A. Storage to Pub/Sub
echo "Configuring Storage to Pub/Sub..."
STORAGE_SA=$(gcloud storage service-agent --project="$PROJECT_ID")
gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$STORAGE_SA" 
    --role="roles/pubsub.publisher"

# B. Force create Eventarc Service Identity via REST API
echo "Ensuring Eventarc Service Identity exists..."
TOKEN=$(gcloud auth print-access-token)
curl -s -X POST -H "Authorization: Bearer $TOKEN" 
     -H "Content-Type: application/json" 
     -d "{}" 
     "https://serviceusage.googleapis.com/v1/projects/$PROJECT_NUMBER/services/eventarc.googleapis.com:generateServiceIdentity"

echo "Waiting 30s for service identity to propagate..."
sleep 30

EVENTARC_SA="service-$PROJECT_NUMBER@gcp-sa-eventarc.iam.gserviceaccount.com"

# Grant Eventarc SA permission to validate the bucket
echo "Granting Eventarc SA storage permissions..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$EVENTARC_SA" 
    --role="roles/eventarc.serviceAgent"

# C. Build & Runtime Permissions
echo "Configuring Build/Runtime permissions..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$COMPUTE_SA" 
    --role="roles/eventarc.eventReceiver"

gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$COMPUTE_SA" 
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$COMPUTE_SA" 
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$COMPUTE_SA" 
    --role="roles/logging.logWriter"

# 3. Deploy the Function
echo "Deploying Cloud Function: rag-ingestion-$ENV..."
# Note: Source is relative to root
gcloud functions deploy rag-ingestion-$ENV 
    --gen2 
    --runtime=python311 
    --region="$REGION" 
    --project="$PROJECT_ID" 
    --source=./data-pipeline/ingestion 
    --entry-point=process_gcs_upload 
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" 
    --trigger-event-filters="bucket=$BUCKET_NAME" 
    --set-env-vars GOOGLE_CLOUD_PROJECT="$PROJECT_ID",DATA_STORE_ID="$DATA_STORE_ID",GOOGLE_CLOUD_LOCATION="global"

echo "✅ Manual deployment complete for $PROJECT_ID!"
