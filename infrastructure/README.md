# Infrastructure as Code (IaC)

This directory contains the Terraform configuration for the JIT Two-Stage Retrieval RAG solution. It is designed to be multi-environment, secure, and highly scalable.

## Design Philosophy
The infrastructure is organized into two primary layers:
1.  **Modules (`modules/`)**: Reusable, atomic building blocks (Project, Storage, Vertex AI, IAP). These are agnostic of the environment.
2.  **Environments (`environments/`)**: Specific configurations for `stage` and `prod`. Each environment maps to a unique GCP Folder ID, allowing for strict isolation between development and production.

## Directory Structure
- `modules/project`: Handles project creation, folder placement, and billing attachment.
- `modules/storage`: Sets up GCS buckets for document ingestion and user feedback.
- `modules/vertex_ai`: Initializes Vertex AI Search (Discovery Engine) and BigQuery datasets.
- `environments/stage`: Staging environment configuration.
- `environments/prod`: Production environment configuration.
- `tests/`: Validation scripts for the IaC code.

## Prerequisites
1.  **GCP Projects**: Manually create two GCP projects (Stage and Prod) via the Google Cloud Console.
2.  **Terraform**: Version 1.5+ installed locally.
3.  **Bootstrap**: Run `scripts/bootstrap.sh` for each project to enable APIs and create the state bucket.
4.  **Identity-Based Access (ADC)**: Since many organizations disable service account keys (`constraints/iam.managed.disableServiceAccountKeyCreation`), this repository is configured to use your **User Identity**.
    -   You **MUST** set a quota project for the Discovery Engine API:
        ```bash
        gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>
        ```
    -   The Terraform provider is explicitly configured with `user_project_override = true` and `billing_project = var.project_id` to ensure API calls are billed to the project context, resolving persistent `403` errors.

## How to Deploy
1.  **Initialize**:
    ```bash
    cd infrastructure/environments/stage
    terraform init -backend-config="bucket=<YOUR_STAGE_PROJECT_ID>-tf-state"
    ```
2.  **Plan**:
    ```bash
    terraform plan -var="project_id=<YOUR_STAGE_PROJECT_ID>"
    ```
3.  **Apply**:
    ```bash
    terraform apply -var="project_id=<YOUR_STAGE_PROJECT_ID>"
    ```

## Running Tests
Run the infrastructure validation script from the root:
```bash
./infrastructure/tests/validate_infra.sh
```
