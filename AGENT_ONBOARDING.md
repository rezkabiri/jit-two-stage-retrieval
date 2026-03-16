# Agent Onboarding & System Overview: JIT Two-Stage Retrieval

Welcome, Agent. This document provides a comprehensive map of the **JIT Two-Stage Retrieval Agentic RAG** repository. Use this to orient yourself before building features, debugging, or performing refactors.

---

## 🎯 System Mission
The goal of this application is to provide a **production-grade, secure, and high-fidelity RAG (Retrieval-Augmented Generation) solution**. It leverages a unique **Two-Stage Architecture** to ensure that data is not only retrieved efficiently but also reasoned over and filtered for security (RBAC) before being presented to the user.

---

## 🏗️ High-Level Architecture
The system follows a classic decoupled architecture optimized for Google Cloud:
1.  **Frontend**: React Chat UI for user interaction.
2.  **State 2 (Agent Logic)**: Google ADK-powered agent that handles reasoning, reranking, and citation.
3.  **Stage 1 (Retrieval)**: Vertex AI Search (Discovery Engine) providing high-performance document retrieval.
4.  **Security**: Identity-Aware Proxy (IAP) for authentication + RBAC metadata filtering at the retrieval layer.
5.  **Data Engine**: Automated pipeline for metadata-enriched ingestion.

---

## 📁 Codebase Directory Breakdown

### 1. `/app` (Application Layer - Agent)
This is the core "intelligence" of the system.
- `agent.py`: Defines the ADK `root_agent`. Orchestrates the two-stage process.
- `tools/retriever.py`: The `stage_1_retrieval` tool. Connects to Vertex AI Search and applies role-based filters (`user_email`).
- `GEMINI.md`: Strict technical mandates for the agent (security, grounding, citations).
- `Dockerfile`: Containerizes the agent for Cloud Run deployment.

### 2. `/frontend` (User Interface)
A modern React application built with Vite and TypeScript.
- `src/App.tsx`: Main chat interface and connection logic to the agent backend.
- `src/components/`: Reusable UI elements for messages, input, and citations.

### 3. `/data-pipeline` (ETL & Ingestion)
Handles the "G" in RAG by ensuring documents are properly ingested and tagged.
- `ingestion/main.py`: Main entry point for syncing GCS documents to Vertex AI Search.
- `ingestion/parser.py`: Logic for extracting text and metadata (roles, categories).
- `schemas/`: Defines the metadata structure for the data store.

### 4. `/infrastructure` (Infrastructure as Code)
Multi-environment Terraform configuration providing a repeatable, audition-ready cloud stack.
- **Deep Dive: Infrastructure Structure**:
    - `modules/`: Contains atomic building blocks for the architecture.
        - `project`: Configures GCP project APIs and Artifact Registry.
        - `storage`: Sets up GCS buckets for raw and parsed documents.
        - `vertex_ai`: Initializes Discovery Engine (Vertex AI Search) and BigQuery feedback datasets.
        - `iap`: Configures Identity-Aware Proxy for secure user access to the UI.
    - `environments/`: Strictly isolated configurations for `stage` and `prod`.
        - Each environment uses a remote GCS backend for state management.
        - `main.tf` in each env calls the shared modules with environment-specific parameters (e.g., machine types, folder IDs).
    - `README.md`: Step-by-step guide for running the bootstrap script and performing a fresh Terraform deployment.

### 5. `/cicd` (Continuous Integration & Deployment)
Provides high-velocity, safe deployments using Google Cloud Build.
- **Deep Dive: CI/CD Workflow (`cloudbuild.yaml`)**:
    1.  **Preparation**: Pulls the `latest` images to use as a docker layer cache, significantly speeding up build times.
    2.  **Build & Push**: Builds the Agent and UI images concurrently. Tags them with both `SHORT_SHA` (for specific deployments) and `latest`.
    3.  **Staging Deployment**: Uses `gcloud run deploy` to push the new images to the `stage-agent` and `stage-ui` services.
    4.  **Evaluation Gate**: Triggers the `make eval` command. This run uses the newly deployed staging agent to verify that recent changes haven't regressed quality or broken security guardrails.
    5.  **Production Promote**: (Conditional) Upon manual approval and successful evaluation, the pipeline pushes the *locally verified* staging images to the Production Artifact Registry and redeploys the production Cloud Run services.
- `README.md`: Details the required Cloud Build substitutions (e.g., `_STAGING_PROJECT_ID`) and secret management.
### 6. Configuration & Secret Management
The bridge between Infrastructure and the Runtime Application.
- **Environment Variables**:
    - Infrastructure modules output service URLs and resource IDs.
    - CI/CD pulls these values into runtime environment variables for Cloud Run.
    - Key variables include `GOOGLE_CLOUD_PROJECT`, `DATA_STORE_ID`, and `ADK_PORT`.
- **Secret Manager**:
    - Sensitive values (like API keys if any) are stored in GCP Secret Manager and mounted as volumes or environment variables in Cloud Run.
    - Managed via Terraform in `infrastructure/modules/project/main.tf`.

### 6. `/eval` (AI Quality Assurance)
- `eval_config.json`: Thresholds and criteria for agent assessment (hallucination checks, tool accuracy).
- `eval_cases.json`: Gold-standard datasets for testing the RAG accuracy.

### 7. `/scripts` & Root
- `Makefile`: **Crucial Developer Entry Point**. Commands for `install`, `playground`, `test`, `eval`, and `deploy`.
- `bootstrap.sh`: One-time setup script for GCP projects (enabling APIs, etc.).
- `DESIGN_SPEC.md` / `PLAN.md`: Strategic blueprints for the project.

---

## 🔑 Operational Workflows

### 🛠️ Local Development
1.  **Bootstrap**: Run `scripts/bootstrap.sh` to prep your GCP environment.
2.  **Playground**: Run `make playground` to interact with the agent via the ADK web console.
3.  **Tests**: Run `make test` to execute unit and integration suites across all modules.

### 🚀 Deployment
- **Staging**: `make deploy-stage` triggers the Cloud Build pipeline.
- **Production**: Follow the production promote step in the Cloud Build UI after evaluation passes.

---

## 🛡️ Security Implementation
- **Zero-Trust**: All traffic is guarded by Google Cloud IAP.
- **RBAC**: The agent extracts the user's email from the session headers and passes it to the `retriever` tool. The tool uses this to inject a `filter` query into the Vertex AI Search request, ensuring users only see documents they are authorized to access.

---

## 🧠 Guidance for Future Agents (How to improve/debug)
- **Adding a new Tool**: Place it in `app/tools/`, define it with the `@tool` decorator, and register it in `app/agent.py`.
- **Modifying UI**: React components are in `frontend/src/components`. Use Tailwind for styling if requested.
- **Debugging Retrieval**:
    1. Check `app/tools/retriever.py` for filter construction.
    2. Use `make playground` to inspect tool calls in real-time.
- **Updating Infra**: Modify the modules in `infrastructure/modules/` and run `terraform plan` in the appropriate environment directory.

---
*Generated by Antigravity - March 16, 2026*
