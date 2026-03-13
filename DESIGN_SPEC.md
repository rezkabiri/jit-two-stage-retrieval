# DESIGN_SPEC: JIT Two-Stage Retrieval Agentic RAG

## Overview
This project implements a high-scale, production-grade Agentic RAG (Retrieval-Augmented Generation) solution on Google Cloud Platform. It utilizes a **two-stage retrieval architecture** to balance performance, cost, and extreme precision.

*   **Stage 1 (Retrieval):** High-speed search over a large vector/document space using **Vertex AI Search**. Security is enforced via **RBAC-based metadata filtering**, ensuring users only retrieve documents they are authorized to see.
*   **Stage 2 (Reasoning & Reranking):** An **ADK-based agent** receives the top results from Stage 1. It performs deep reasoning and reranking using **Cross-Encoder embeddings** to ensure the final response is contextually accurate, grounded, and high-fidelity.

The solution is protected by **Identity-Aware Proxy (IAP)**, which provides secure, identity-based access without the need for custom auth logic in the application.

## Example Use Cases
Refer to `docs/industry_use_cases_rag.md` for detailed scenarios in:
1.  **Global Financial Services**: Compliance-heavy research and KYC.
2.  **Hyperscale SaaS Support**: Self-healing diagnostic agents for cloud infrastructure.
3.  **Legal Tech**: Secure M&A discovery with strict ethical walls.

## Technical Architecture

### 1. Identity & RBAC
*   **Authentication**: Google Identity Platform + Identity-Aware Proxy (IAP).
*   **Authorization**: The Agent extracts the `X-Goog-Authenticated-User-Email` header. This email is mapped to a role/permission set which is injected as a filter into the Stage 1 retrieval query.

### 2. The Data Engine (ETL)
*   **Source**: GCS Buckets (Staging/Production).
*   **Trigger**: Eventarc/GCS notification kicks off a Cloud Build or Cloud Function.
*   **Processing**: Python-based ETL parses documents, extracts metadata, assigns RBAC tags based on folder structure, and indexes into Vertex AI Search.
*   **Location Strategy**: Discovery Engine (Vertex AI Search) is globally managed, while BigQuery and GCS reside in the regional bucket/dataset for latency and data residency compliance.

### 3. Feedback Loop
*   **UI**: Thumbs-up/down buttons for every agent response.
*   **Storage**: Feedback and conversation traces are logged to **BigQuery** for long-term analytics and reranker fine-tuning.

### 4. Implementation Constraints (Infrastructure)
*   **API Activation Sequence**: `discoveryengine.googleapis.com` must be activated **before** Terraform can manage Data Store resources. This is handled in `scripts/bootstrap.sh`.
*   **Discovery Engine Scope**: Multi-environment separation is strictly enforced at the project level, as Vertex AI Search configurations are project-scoped.
*   **Authentication (ADC & Quota)**: When using Application Default Credentials (ADC) without service account keys, the Terraform provider **must** use `user_project_override = true` and `billing_project = var.project_id`. This ensures the Discovery Engine API has a valid quota project context to avoid `403` errors.

## Tools Required
*   **`stage_1_retrieval`**: A tool for the ADK agent to query Vertex AI Search with RBAC filters.
*   **`record_feedback`**: A tool to asynchronously log user feedback to BigQuery.
*   **`cross_encoder_reranker`**: Internal logic to score and re-order Stage 1 results.

## Constraints & Safety Rules
*   **Data Leakage**: The agent MUST NOT access or summarize documents if the RBAC metadata filter returns zero results or if the user identity is missing.
*   **Grounding**: Every response must cite the source document from the retrieved context.
*   **Hallucinations**: If no relevant context is found after reranking, the agent must state it does not have the information.

## Success Criteria (Evaluation)
*   **Retrieval Recall**: Top 5 results in Stage 1 must contain the answer 95% of the time.
*   **Grounding Score**: > 0.9 (measured via ADK Eval and LLM-as-a-judge).
*   **Latency**: End-to-end response < 4 seconds for standard queries.
*   **RBAC Integrity**: Zero instances of "unauthorized document" appearing in Stage 2 context during red-teaming.

## CI/CD Pipeline
*   **Tool**: Google Cloud Build.
*   **Flow**:
    1.  Commit to `main` -> Deploy to **Staging** Folder.
    2.  Run `app/tests/` and `data-pipeline/tests/`.
    3.  Run **ADK Eval** (`make eval`) against staging.
    4.  Upon passing quality gates -> Deploy to **Production** Folder.
