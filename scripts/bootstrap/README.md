# Bootstrap Scripts

This directory contains scripts for initializing the GCP environment and setting up the foundations for Terraform and CI/CD.

## `bootstrap.sh`

The `bootstrap.sh` script is designed to handle the "cold start" of a GCP project. It performs the following critical tasks:
1.  **Enables Critical APIs**: `Vertex AI`, `Discovery Engine`, `IAM`, `IAP`, `Cloud Build`, `Storage`, etc.
2.  **Creates Terraform State Bucket**: A dedicated bucket for storing remote Terraform state files with versioning enabled.
3.  **Sets Project Context**: Ensures the gcloud environment is correctly configured for the target project.

### Dual-Environment Strategy
This repository supports two primary environments, each requiring its own bootstrap process:
- **Staging (`stage`)**: For integration testing and evaluation.
- **Production (`prod`)**: The live environment for end users.

### How to Run
You must run the bootstrap script for **each** project before applying Terraform.

**For Staging:**
```bash
./scripts/bootstrap/bootstrap.sh <STAGING_PROJECT_ID> [REGION]
```

**For Production:**
```bash
./scripts/bootstrap/bootstrap.sh <PRODUCTION_PROJECT_ID> [REGION]
```

### Purpose in the Pipeline
While primarily used for local project initialization, this script can be incorporated into a CI/CD pipeline to ensure that any new environment (e.g., a dynamic "PR Preview" environment) is correctly provisioned with the necessary GCP services before Terraform runs.
