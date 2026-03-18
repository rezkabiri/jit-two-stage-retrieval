# JIT Two-Stage Retrieval Agentic RAG

A high-performance, production-grade Agentic RAG solution on Google Cloud Platform, featuring a two-stage retrieval architecture with built-in RBAC and automated evaluation.

## 🚀 Key Features

```mermaid
graph LR
    User --> Agent[ADK Agent]
    Agent --> Stage1[Vertex AI Search]
    Stage1 --> Stage2[Vertex AI Ranking API]
    Stage2 --> Response[Grounded Answer]
```

- **Two-Stage Retrieval**: Stage 1 (Fast Retrieval via Vertex AI Search) + Stage 2 (Deep Reasoning & Reranking via ADK Agent).
- **Identity-Aware Proxy (IAP)**: Zero-trust authentication out-of-the-box.
- **RBAC-Aware Filtering**: Security tags are injected at the retrieval layer to ensure data isolation.
- **Multi-Environment CI/CD**: Fully automated deployment to `stage` and `prod` GCP folders via Google Cloud Build.
- **Data Engine**: Automated ETL pipeline for GCS-to-Vertex AI Search ingestion with metadata enrichment.

## 📁 Repository Structure
```text
├── app/                # ADK Agent (Stage 2 logic)
├── frontend/           # React Chat UI
├── data-pipeline/      # ETL & Ingestion (Python)
├── infrastructure/     # Terraform IaC (Stage & Prod)
├── cicd/               # Deployment Pipeline (Cloud Build)
├── eval/               # ADK Evaluation Sets
├── scripts/            # Bootstrap & Utility scripts
└── docs/               # Technical use cases & documentation
```

## 🚀 CI/CD & Evaluation Gate

This project implements a multi-stage deployment pipeline using **Google Cloud Build**, ensuring that only high-quality, validated models reach production.

```mermaid
graph LR
    Build[Build Images] --> DeployStaging[Deploy to Staging]
    DeployStaging --> EvalGate[ADK Evaluation Gate]
    EvalGate -- "Pass" --> Promote[Promote to Production]
    EvalGate -- "Fail" --> Block[Block Deployment]
    Promote --> DeployProd[Deploy to Production]
```

### Pipeline Flow
1.  **Build & Push**: Docker images for the Agent and UI are built and pushed to the Staging Artifact Registry.
2.  **Staging Deployment**: The Agent is deployed to a Staging Cloud Run service.
3.  **Evaluation Gate (Crucial)**: The pipeline executes `make eval` against the Staging environment.
    *   Uses **ADK Evaluation** with the "Golden Set" (`eval/eval_cases.json`).
    *   Measures Recall, Grounding Score, and Latency.
    *   **Deployment Blocker**: If the evaluation scores fall below the defined thresholds, the pipeline fails, and the production promotion is blocked.
4.  **Production Promotion**: Upon successful evaluation, images are tagged and pushed to the Production Artifact Registry.
5.  **Production Deployment**: The validated Agent and UI are deployed to the Production Cloud Run environment.

## 🛠️ Quick Start

### 1. Bootstrap the Environment
Before running Terraform, initialize each GCP project:
```bash
./scripts/bootstrap/bootstrap.sh <PROJECT_ID> [REGION]
```

### 2. Local Development Setup
Quickly spin up the backend and frontend for local testing:
```bash
# Setup dependencies and proxy
./scripts/local-dev/setup_local.sh

# Follow the instructions in scripts/local-dev/README.md to start the services
```

### 3. Accessing the Environments (Staging/Prod)
Since this project uses custom domains (`rag-stage.example.com`) and Identity-Aware Proxy (IAP), follow these steps to access the web UI:

#### **Staging DNS Workaround**
If you haven't mapped a real domain, you must point your local `hosts` file to the Load Balancer IP:
1.  **Get the IP**: Run `terraform output load_balancer_ip` in `infrastructure/environments/stage`.
2.  **Edit Hosts**: Add the following to `/etc/hosts` (Mac/Linux) or `C:\Windows\System32\drivers\etc\hosts` (Windows):
    ```text
    <LB_IP_ADDRESS> rag-stage.example.com
    ```
3.  **Bypass SSL Warning**: Navigate to `https://rag-stage.example.com`. Since we use a self-signed certificate fallback for staging, click **Advanced** -> **Proceed (unsafe)**.

### 4. Provision Infrastructure
Deploy the staging environment:
```bash
cd infrastructure/environments/stage
terraform init
terraform apply
```

### 5. Unified Commands
Use the `Makefile` in the root for common development tasks:
- `make install`: Install dependencies.
- `make playground`: Start the interactive ADK chat.
- `make test`: Run all unit and integration tests.
- `make eval`: Run AI quality evaluations.
- `make deploy-stage`: Trigger the staging deployment pipeline.

## 📖 Documentation
- [Technical Design Specification](DESIGN_SPEC.md)
- [Infrastructure Guide](infrastructure/README.md)
- [Bootstrap Guide](scripts/README.md)
- [Industry Use Cases](docs/industry_use_cases_rag.md)
