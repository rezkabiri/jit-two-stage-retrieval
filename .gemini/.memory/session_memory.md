# Consolidated Agent Memory & Onboarding: JIT Two-Stage Retrieval

## 📅 Last Updated: March 20, 2026
**Status**: Production-ready core infrastructure, stabilized ETL, and parallelized CI/CD.

---

## 🏗️ System Architecture (High-Level)
The system follows a decoupled architecture optimized for Google Cloud:
1.  **Frontend**: React Chat UI (Vite + TypeScript).
2.  **Stage 2 (Agent Logic)**: ADK-powered `SequentialAgent` (`Retriever` -> `Reranker`) using Gemini 2.0 Flash.
3.  **Stage 1 (Retrieval)**: Vertex AI Search providing high-performance search with RBAC metadata filtering.
4.  **Security**: IAP for Auth + Identity extraction for injected filters.
5.  **Data Engine**: Automated GCS-to-Vertex indexing via Cloud Functions (v2).
6.  **Feedback Loop**: BigQuery telemetry (`agent_feedback`) for continuous improvement.

---

## 📁 Codebase Directory Map
- `/app`: Core Agent logic, tools, and FastAPI backend.
- `/frontend`: React UI.
- `/data-pipeline`: Ingestion ETL logic.
- `/infrastructure`: Multi-environment Terraform (Stage/Prod).
- `/cicd`: Cloud Build pipeline configurations.
- `/eval`: ADK Golden Set for quality assessment.
- `/tests`: Comprehensive suites (Unit, Infra, E2E).

---

## 👤 User Engineering Style
- **Verification First**: Local `terraform plan/apply` is mandatory before pushing.
- **Production-Grade**: Prefers Secret Manager and strict Least Privilege IAM.
- **Test-Driven**: Expects every module to have a dedicated test suite and a descriptive `README.md`.
- **Transparency**: High value on deep-dive RCA (Root Cause Analysis) for cloud-native errors (404/429/403).

---

## 🔍 Historical Bug Chain & RCAs
### 1. Regional Vertex AI 404s
- **Cause**: "Publisher Models" restricted in `us-central1`.
- **Solution**: Migrated to **Global Gemini API (AI Studio)** backend via Secret Manager using `gemini-2.0-flash`.

### 2. Vertex AI DataStore Deletion Loop
- **Cause**: ~2-hour deletion lock preventing ID reuse.
- **Solution**: Incremented version keeper in Terraform `random_id` (current: **v32**).

### 3. Manual Sync & Environment Reset
- **Cause**: `gcloud run services update` cleared existing environment variables.
- **Solution**: Always use `--update-env-vars` or restore the full set (`DATA_STORE_ID`, `PROJECT_ID`, `LOCATION`).

---

## 🚀 Efficiency Guidelines for Future Sessions
1.  **Escape YAML**: Always use `$$` for shell variables in `cloudbuild.yaml`.
2.  **Verify Models**: Perform `curl .../models?key=...` to check quota/availability before switching versions.
3.  **TF Observability**: Maintain `data_store_id` in top-level outputs for instant verification.
4.  **Python Packages**: Ensure `__init__.py` exists in all subfolders involved in CI testing.

---

## 🛠 Skills & Resources
- **GCP Architect**: Essential for IAM and service-level verification.
- **ADK Dev Guide**: Recommended for maintaining SDK alignment.
- **Makefile**: The primary entry point for `install`, `test`, and `deploy`.
