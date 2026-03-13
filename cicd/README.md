# CI/CD: Multi-Stage Deployment Pipeline

This directory contains the Google Cloud Build configuration for automated testing, evaluation, and deployment of the JIT Two-Stage Retrieval RAG system.

## GitHub Integration (Step-by-Step)

### 1. Connect the Repository
1.  **GCP Console**: Go to **Cloud Build** > **Repositories** > **2nd Gen**.
2.  **Create Connection**: Select **GitHub** and follow the OAuth flow to authorize Google Cloud.
3.  **Link Repository**: Select your `jit-two-stage-retrieval` repository.

### 2. Create the Build Trigger
1.  **GCP Console**: Go to **Cloud Build** > **Triggers** > **Create Trigger**.
2.  **Name**: `deploy-to-staging-on-push`.
3.  **Event**: Push to a branch.
4.  **Source**: Your connected GitHub repo.
5.  **Branch**: `^main$`.
6.  **Configuration**: **Cloud Build configuration file (yaml/json)**.
7.  **Location**: `/cicd/cloudbuild.yaml`.

### 3. Add Critical Substitutions
In the **Substitutions** section of the trigger, add these variables:
- `_ENV`: `stage`
- `_REGION`: `us-central1`
- `_STAGING_PROJECT_ID`: `<YOUR_STAGE_PROJECT_ID>`
- `_BILLING_ACCOUNT`: `<YOUR_BILLING_ACCOUNT_ID>`

### 4. Grant Cloud Build Permissions
Cloud Build needs to be able to deploy to Cloud Run, Functions, and manage Service Accounts. 
Go to **IAM & Admin** > **IAM** and grant the **Cloud Build Service Account** (`<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com`) these roles:
- `roles/run.admin`
- `roles/cloudfunctions.developer`
- `roles/iam.serviceAccountUser`
- `roles/artifactregistry.admin`
- `roles/storage.admin`
- `roles/discoveryengine.admin`

## Pipeline Architecture
The pipeline follows a **Promotion-Based Model**:
1.  **Commit to `main`**: Triggers a build for the **Staging** environment.
2.  **Staging Deployment**: Builds and deploys the Agent (Cloud Run), Frontend (Cloud Run), and ETL (Cloud Functions).
3.  **Quality Gate (Eval)**: Runs the ADK evaluation suite against the staging environment.
4.  **Production Promotion**: (Manual or Automated) Deploys the validated staging artifacts to the **Production** environment.

## Trigger Configuration
To set up the trigger in the GCP Console (or via Terraform):
1.  **Repository**: Connect your GitHub/GitLab repo.
2.  **Configuration**: Use `cicd/cloudbuild.yaml`.
3.  **Substitutions**:
    - `_ENV`: `stage` (default)
    - `_REGION`: `us-central1`
    - `_STAGING_FOLDER_ID`: Your staging folder ID.
    - `_PROD_FOLDER_ID`: Your production folder ID.

## Cloud Build Steps
- **Build**: Uses multi-stage Docker builds to optimize image size.
- **Push**: Stores images in the project's **Artifact Registry** (`rag-repo`).
- **Deploy**: Uses `gcloud run deploy` and `gcloud functions deploy`.
- **Eval**: Runs `adk eval` to ensure RAG performance thresholds are met before promotion.

## Testing & Validation
- **Unit Tests**: `pytest app/tests/` and `pytest data-pipeline/tests/`.
- **Frontend Tests**: `npm test` inside the `frontend/` directory.
- **Evaluation**: The pipeline will fail if the ADK eval score drops below the threshold (e.g., 0.8).
