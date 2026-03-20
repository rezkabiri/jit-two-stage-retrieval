#!/bin/bash
# infrastructure/tests/validate_infra.sh: Validation script for IaC and Live Resources

set -e

PROJECT_ID=""
ENV=""

usage() {
  echo "Usage: $0 --project PROJECT_ID --env [stage|prod]"
  exit 1
}

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --project) PROJECT_ID="$2"; shift ;;
    --env) ENV="$2"; shift ;;
    *) usage ;;
  esac
  shift
done

if [[ -z "$PROJECT_ID" || -z "$ENV" ]]; then usage; fi

echo "🔍 Validating Infrastructure for project: $PROJECT_ID ($ENV)"

# 1. Terraform Static Checks
echo "--- Step 1: Static Checks ---"
terraform -chdir=infrastructure/environments/$ENV init -backend=false
terraform -chdir=infrastructure/environments/$ENV validate

# 2. Resource Existence Checks
echo "--- Step 2: Live Resource Checks ---"

# A. Cloud Run Services
echo "Checking Cloud Run services..."
gcloud run services describe rag-agent-$ENV --project=$PROJECT_ID --region=us-central1 > /dev/null
gcloud run services describe rag-ui-$ENV --project=$PROJECT_ID --region=us-central1 > /dev/null
gcloud run services describe rag-ingestion-$ENV --project=$PROJECT_ID --region=us-central1 > /dev/null

# B. BigQuery Tables
echo "Checking BigQuery feedback tables..."
bq show --project_id=$PROJECT_ID agent_feedback.user_feedback > /dev/null
bq show --project_id=$PROJECT_ID agent_feedback.conversations > /dev/null

# C. Secret Manager
echo "Checking Secret Manager..."
gcloud secrets describe gemini-api-key-$ENV --project=$PROJECT_ID > /dev/null

# 3. Security Checks (IAM)
echo "--- Step 3: IAM Verification ---"
COMPUTE_SA=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")-compute@developer.gserviceaccount.com

echo "Checking if Compute SA has BigQuery Data Editor..."
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:$COMPUTE_SA AND bindings.role:roles/bigquery.dataEditor" \
    --format="value(bindings.role)" | grep -q "roles/bigquery.dataEditor"

echo "✅ All infrastructure validations passed!"
