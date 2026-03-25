# Contributing to JIT Two-Stage Retrieval RAG

Welcome to the project! This guide will help you understand the architecture, development workflow, and deployment processes for this Agentic RAG solution.

---

## 🏗️ Architecture Overview

The repository is organized into distinct modules to ensure separation of concerns:

-   **/app**: The core RAG Agent built with Google Agent Development Kit (ADK). It uses FastAPI to serve versioned endpoints.
-   **/frontend**: A React (Vite) chat interface.
-   **/data-pipeline**: A serverless ETL pipeline (Python Cloud Functions) that handles document parsing and RBAC metadata enrichment.
-   **/infrastructure**: Terraform code for provisioning GCP resources across different environments.
-   **/knowledge-base**: The "Golden Dataset" used for sanity checks and RBAC validation.
-   **/tests**: Comprehensive testing suites (Unit, Red Team, E2E).
-   **/scripts**: Operational utilities for bootstrapping, disaster recovery, and security simulations.

---

## 🚀 Getting Started (Cold Start Guide)

To deploy this solution to a brand-new GCP environment:

### 1. Project Strategy
We follow a **Strict Project Isolation** strategy. You must have two separate GCP projects:
-   `your-project-stage`: For CI/CD, security testing, and UAT.
-   `your-project-prod`: The live environment.

### 2. Bootstrapping
Before running Terraform, you must initialize the project APIs and state storage:
```bash
./scripts/bootstrap/bootstrap.sh <YOUR_PROJECT_ID> <REGION>
```

### 3. Provisioning
Deploy the infrastructure using Terraform:
```bash
cd infrastructure/environments/stage
terraform init -backend-config="bucket=<YOUR_PROJECT_ID>-tf-state"
terraform apply
```

---

## 🧪 Testing Strategy

We maintain three tiers of validation. You **must** update the corresponding tests when modifying these components:

| Component | Test Suite Location | When to Update |
| :--- | :--- | :--- |
| **Agent Logic / API** | `app/tests/` | When changing ADK instructions, tool signatures, or FastAPI routes. |
| **RBAC / Security** | `tests/red-team/` | When modifying `app/roles.py` or the security boundaries. |
| **ETL / Parsing** | `data-pipeline/tests/` | When adding support for new file types or changing metadata logic. |
| **Infrastructure** | `infrastructure/tests/` | When adding new GCP resources or changing IAM permissions. |

### Running Tests Locally
```bash
# Run all Python tests
make test
```

---

## 🛣️ API Versioning

We use **Path-Based Versioning**. All breaking changes must be introduced in a new versioned directory.
-   **Current Version**: `/api/v1/`
-   **Structure**: `app/api/v<N>/endpoints/`
-   **Documentation**: See `docs/API_VERSIONING_STRATEGY.md` for more details.

---

## 🛠️ Development Guidelines

1.  **Code Style**: Follow PEP8 for Python and use Prettier for TypeScript/React.
2.  **Environment Variables**: Never hardcode secrets. Use Secret Manager (managed via Terraform in `modules/secrets`).
3.  **Logging**: Use the standard `logging` module. All logs must be structured for Cloud Logging (already configured in `app/main.py`).
4.  **Security First**: Any change affecting `app/roles.py` must be validated by the `scripts/red-team/simulate_security_breach.py` script before promotion.

---

## 🔄 Deployment Pipeline

This project uses **Google Cloud Build** (`cicd/cloudbuild.yaml`).
-   **Triggers**: Any push to the `main` branch triggers the staging pipeline.
-   **Promotion**: Production deployment requires manual approval or a successful completion of the **ADK Evaluation Gate**.

---

## 🆘 Troubleshooting & Ops

-   **Data Corrupted?** Run the DR Rebuild Drill: `./scripts/dr/rebuild_datastore.sh`.
-   **RBAC Issues?** Check the `X-Goog-Authenticated-User-Email` header in the agent logs.
-   **Deployment Failing?** Ensure the `discoveryengine.googleapis.com` API was enabled via the bootstrap script.
