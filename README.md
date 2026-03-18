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

### 3. Provision Infrastructure
Deploy the staging environment:
```bash
cd infrastructure/environments/stage
terraform init
terraform apply
```

### 3. Unified Commands
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
