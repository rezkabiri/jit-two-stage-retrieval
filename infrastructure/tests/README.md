# Infrastructure Validation Tests

## Scope
This folder contains scripts to verify the state of the deployed GCP resources and ensure they match the requirements defined in the Terraform modules.

### Key Components Verified:
- **Resource Existence**: Verifying Cloud Run services, BigQuery tables, and Vertex AI DataStores.
- **Environment Synchronization**: Ensuring that `DATA_STORE_ID` matches across Terraform and the live services.
- **Security & IAM**: Confirming that the Cloud Run service account has the necessary permissions (BigQuery, Discovery Engine, Secrets).

## How to Run
Ensure you are authenticated with `gcloud` and have the project set:
```bash
cd infrastructure/tests
./validate_infra.sh --project [PROJECT_ID] --env [stage|prod]
```

## Expectations
- The script should return a success code only if **all** critical resources are found and IAM permissions are active.
- It should alert if the live `DATA_STORE_ID` on the ingestion function differs from the one defined in the environment's state.
