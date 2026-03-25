# Failure & Recovery Testing

This guide outlines the procedures for validating the resilience and recovery capabilities of the JIT Two-Stage RAG system.

## Disaster Recovery (DR) Rebuild Drill

**Goal**: Validate the "Recovery Time Objective" (RTO) for the Vertex AI Search index. This drill simulates a total data corruption or accidental deletion of the Search Data Store.

### When to Run
- **Quarterly Compliance**: To satisfy production readiness requirements.
- **After Schema Changes**: When changing document metadata structures or indexing configurations.
- **Corrupted State**: If the agent consistently fails to retrieve known documents despite correct RBAC mapping.

### When NOT to Run
- **Peak Hours**: Re-indexing large corpuses can cause temporary retrieval gaps.
- **Production without Approval**: This script performs a destructive `destroy/create` cycle on the Data Store.

### Prerequisites
1. **Google Cloud SDK**: Logged in with `gcloud auth application-default login`.
2. **Terraform**: Installed and initialized in the environment.
3. **Python 3.11+**: With the following requirements installed:
   ```bash
   pip install google-cloud-storage google-cloud-discoveryengine
   ```
4. **Environment Variables**: `GOOGLE_CLOUD_PROJECT` must be set.

### How to Run the Drill

1. **Setup the Environment**:
   Ensure you have the necessary Python packages in your virtual environment:
   ```bash
   pip install -r data-pipeline/ingestion/requirements.txt
   ```

2. **Execute the Drill Script**:
   Run the automated drill script from the root of the repository:
   ```bash
   ./scripts/dr/rebuild_datastore.sh <PROJECT_ID> <ENV> [REGION]
   ```
   *Example*: `./scripts/dr/rebuild_datastore.sh jit-tsr-rag-stage stage us-central1`

### What the Script Does
1. **Force Deletion**: Uses `terraform apply -replace` to trigger a clean recreation of the `rag_data_store` resource.
2. **Re-provisioning**: Terraform creates a new Data Store with a fresh ID (using a random suffix).
3. **Full Re-ingestion**: Triggers `data-pipeline/ingestion/reingest_all.py`, which iterates through the GCS ingestion bucket and pushes every document back into the new index with its associated RBAC metadata.

### Success Criteria
- Script completes without errors.
- Vertex AI Search Console shows documents being indexed.
- Grounding is restored for a sample query (e.g., "what is global economy is characterized by in 2025?") within 10-15 minutes.

---

## Upcoming: Fault Injection (Chaos Engineering)
*See todo.md for implementation status.*
- **Synthetic Latency**: Simulating slow model responses.
- **Service Outages**: Simulating partial Ranking API failures to verify graceful fallback.
