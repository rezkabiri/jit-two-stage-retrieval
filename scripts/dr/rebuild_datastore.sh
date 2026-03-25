#!/bin/bash
# scripts/dr/rebuild_datastore.sh: Disaster Recovery Drill for Data Store Rebuild
# Automates the deletion, re-provisioning, and full re-ingestion of the Search index.

set -e

PROJECT_ID=$1
ENV=$2 # stage or prod
REGION=${3:-us-central1}

if [[ -z "$PROJECT_ID" || -z "$ENV" ]]; then
    echo "❌ ERROR: Missing arguments."
    echo "Usage: $0 <PROJECT_ID> <ENV> [REGION]"
    exit 1
fi

echo "🚨 STARTING DISASTER RECOVERY DRILL: Data Store Rebuild ($ENV)"
echo "--------------------------------------------------------"

# 1. Initialize Terraform
echo "📦 Initializing Terraform..."
cd infrastructure/environments/"$ENV"
terraform init -backend=false # Using -backend=false for safety in drill, or assume initialized

# 2. Force Recreate the Data Store
# We use -replace to force a destroy/create cycle on the specific resource
echo "🧨 Destroying and Re-provisioning Data Store..."
terraform apply 
    -var="project_id=$PROJECT_ID" 
    -var="region=$REGION" 
    -replace="module.vertex_ai.google_discovery_engine_data_store.rag_data_store" 
    -auto-approve

# 3. Get the new Data Store ID
DATA_STORE_ID=$(terraform output -raw data_store_id)
INGESTION_BUCKET=$(terraform output -raw ingestion_bucket)

echo "✅ New Data Store ID: $DATA_STORE_ID"
echo "✅ Ingestion Bucket: $INGESTION_BUCKET"

# 4. Run Full Re-ingestion from Knowledge Base
echo "🔄 Triggering full corpus re-ingestion..."
cd ../../../ # Back to root
export PYTHONPATH=$PYTHONPATH:$(pwd)/data-pipeline/ingestion

# Note: Using the temporary venv if available, or assume environment is ready
python3 data-pipeline/ingestion/reingest_all.py 
    --project "$PROJECT_ID" 
    --bucket "$INGESTION_BUCKET" 
    --datastore "$DATA_STORE_ID"

echo "--------------------------------------------------------"
echo "🏁 DISASTER RECOVERY DRILL COMPLETE"
echo "Grounding should be restored within minutes as Vertex AI Search indexes the documents."
