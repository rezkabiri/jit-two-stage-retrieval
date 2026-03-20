# FDE Repository Assessment: JIT Two-Stage Retrieval Agent

This report provides a detailed audit of the repository against the **Full-stack Deep Engineering (FDE) Rubric**.

## Assessment Table

| Category | Item | Pertaining Repo Location / Evidence |
| :--- | :--- | :--- |
| **[AI/ML ENGINEERING]** | Agentic & Multi-Agent Systems | **`app/agent.py`** (Lines 62-69): Implementation of a `SequentialAgent` workflow orchestrating Retriever and Reranker roles. |
| | Retrieval & Data Engineering (RAG) | **`app/tools/retriever.py`** (Lines 14-66), **`app/reranker.py`** (Lines 56-107), and **`data-pipeline/ingestion/parser.py`** for ETL and RBAC mapping metadata. |
| | Model Selection & Tuning | **`app/agent.py`** (Model instantiation) and **`app/reranker.py`**. The specific logic in `app/agent.py` shows intentional choice of models per task. |
| | LLM Ops and Evaluation | **`eval/eval_cases.json`** (Base evaluation set), **`app/tools/feedback.py`** (Lines 49-92) for Conversation logging, and **`infrastructure/modules/monitoring/main.tf`** (Lines 65-79). |
| | Domain-Applied AI/ML Expertise | **`docs/industry_use_cases_rag.md`**: Detailed mapping of RAG solution to Finance, SaaS, and Legal verticals. |
| **[SCOPING AND DOCUMENTATION]** | Problem Definition | **`README.md`** (Lines 1-53) and **`docs/DESIGN_SPEC.md`** provide clear business and technical problem context. |
| | Technical Scope & Constraints | **`docs/DESIGN_SPEC.md`** defines system boundaries, API sequences, and IaC constraints. |
| | Stakeholder Alignment & Success Criteria | **`docs/DESIGN_SPEC.md`** (Lines 76-81): Explicit performance and grounding success metrics. |
| | System Design Artifacts | **`docs/DESIGN_SPEC.md`** and **`data-pipeline/README.md`** (Mermaid architecture diagrams). |
| | Decision Records | **`docs/ADR_MODEL_PROVIDER_FLEXIBILITY.md`**: ADR detailing logic for switching between AI Studio and Vertex API and managing Quota vs SLA trade-offs. |
| | API Documentation | **`app/main.py`** (FastAPI `app` instantiation) provides automatic Swagger/OpenAPI docs at `/docs`. |
| | Operational Documentation | **`scripts/bootstrap/README.md`** and **`infrastructure/README.md`** for setup and deployment guiding. |
| **[SECURITY, PRIVACY, COMPLIANCE]** | Authentication & Authorization | **`infrastructure/modules/cloud_run/main.tf`** (Lines 154-159) for IAP configuration and **`app/tools/retriever.py`** (Lines 39-49) for RBAC filtering logic based on IAP headers. |
| | Infrastructure & Network Security | **`infrastructure/modules/cloud_run/main.tf`** (Line 37): Usage of `INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER` to restrict access. |
| | Data Protection & Privacy | **`data-pipeline/ingestion/parser.py`** (Lines 22-46): Automatic RBAC tag assignment based on folder hierarchy during ingestion. |
| | AI-Specific Security | **`app/agent.py`** (Lines 44-52): Hardcoded grounding and safety instructions to prevent hallucinations and strictly adhere to provided roles. |
| | Compliance & Governance | **`app/tools/feedback.py`** (Lines 49-92): Full telemetry of LLM inputs, outputs, and user feedback stored into BigQuery for audits and improvements. |
| **[RELIABILITY & RESILIENCE]** | Availability Design | **`infrastructure/modules/cloud_run/main.tf`** (Lines 33-83): Redundant service configuration with health checks. |
| | Observability | **`infrastructure/modules/monitoring/main.tf`**: Cloud Monitoring dashboard for latency, error rates, and request counts of the deployed services. |
| | Failure & Recovery Testing | <span style="color:red">**NOT FOUND**</span> |
| | Graceful Degradation | **`app/reranker.py`** (Lines 104-107): Fallback to initial Stage 1 results if the semantic reranker fails. |
| **[PERFORMANCE & COST OPTIMIZATION]** | Scalability & Elasticity | **`infrastructure/modules/cloud_run/main.tf`** (Lines 49-54): Configurable CPU/Memory limits and regional scaling leveraging serverless autoscaling. |
| | Resource Efficiency | The usage of specific optimal models for specific tasks (e.g. Gemin Flash vs Pro) outlined in **`docs/ADR_MODEL_PROVIDER_FLEXIBILITY.md`** and **`app/agent.py`** for extreme RPD scale. |
| | AI Cost Management | Addressed in **`docs/ADR_MODEL_PROVIDER_FLEXIBILITY.md`**: balancing AI Studio free tier limits during sandbox use and Vertex AI for production workload costs. |
| **[OPERATIONAL EXCELLENCE]** | CI/CD & Deployment | **`cicd/cloudbuild.yaml`**: Multi-stage, parallel build and deployment pipeline with manual promotion gates to Prod. |
| | Infrastructure as Code | **`infrastructure/`** directory contains modularized Terraform modules for multi-environment (Stage/Prod) infrastructure definitions. |
| | AI Lifecycle Management | **`eval/eval_cases.json`** and **`Makefile`** (`make eval` target) for automated quality gating. |
| | Testing & Quality Engineering | **`app/tests/`**, **`data-pipeline/tests/`**, and **`infrastructure/tests/validate_infra.sh`**. End to End tests present in **`tests/e2e/test_rbac_security.py`**. |
| **[DESIGNING FOR CHANGE]** | Modularity & Abstraction | **`app/agent.py`**: Decoupled Sequential agent roles (Planner, Retriever, Reranker) allowing independent updates to logic chains. |
| | Configuration Management | **`infrastructure/environments/`** parameterization via Terraform variables, and Model alias configurations using `USE_VERTEX_AI` environment variables. |
| | API Design & Versioning | **`app/main.py`**: Standardized and extensible FastAPI endpoint structure. |
| | Extensibility | **`app/tools/`** implementation where we can easily plug out and plug in new capabilities like `record_feedback` or `stage_1_retrieval`. |
