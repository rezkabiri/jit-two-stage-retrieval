# Session Memory: Production Agentic RAG Evolution

## 📅 Session Date: March 19-20, 2026
**Status**: Production-ready core infrastructure, stabilized ETL, and parallelized CI/CD.

---

## 🛠 What We Built & Did
We productionized a **Secure Two-Stage Retrieval RAG** on GCP using the Google ADK.
- **Stage 1 (Search)**: Vertex AI Search with RBAC metadata filtering (`role: ANY(...)`).
- **Stage 2 (Rerank)**: ADK SequentialAgent (`Retriever` -> `Reranker`) with Gemini 2.0 Flash.
- **Security**: Zero-trust via IAP; RBAC derived from `X-Goog-Authenticated-User-Email`.
- **Infrastructure**: Multi-environment Terraform (Stage/Prod) with a new **Secret Manager** module for API keys.
- **ETL Pipeline**: Cloud Function (v2) triggered by GCS uploads, performing markdown/PDF parsing and Vertex AI indexing.
- **Feedback Loop**: BigQuery telemetry (`agent_feedback`) for conversation traces and thumbs up/down events.
- **CI/CD**: Cloud Build pipeline with parallelized testing (Agent core, ETL parser, Terraform validation).

---

## 👤 User Style & Preferences
- **Verification First**: High value on running `terraform plan` and `apply` locally to verify logic before committing/pushing.
- **Production-Grade**: Prefers secrets in Secret Manager over plain env vars; strict on IAM permissions (Least Privilege).
- **Comprehensive Testing**: Expects dedicated test suites per folder with clear `README.md` documentation for scope and execution.
- **Direct & Transparent**: Prefers technical deep-dives into 404/429 errors rather than generic fixes.

---

## 🔍 The Chain of Bugs & Lessons Learned
### 1. The Regional 404 Trap
- **Mistake**: Initially tried using Vertex AI's "Publisher Models" in `us-central1` which were restricted or unavailable.
- **Chain**: Switching to `GOOGLE_GENAI_USE_VERTEXAI=true` led to 404s -> Debugged via `ListModels` -> Discovered experimental models like `gemini-3-flash` have tiny quotas (20 RPD).
- **Fix**: Migrated to the **Global Gemini API (AI Studio)** backend via Secret Manager using `gemini-2.0-flash`.

### 2. The Vertex AI Search "Deletion Loop"
- **Problem**: Vertex AI DataStores have a ~2-hour deletion window. Recreating a store with the same ID immediately fails.
- **Chain**: Terraform `apply` failed repeatedly -> Bumped versions from `v27` to `v32` to force unique IDs.
- **Prevention**: Use a `random_id` with a version `keeper` in Terraform to force clean IDs during rapid iteration.

### 3. The "Manual Sync" Regressions
- **Mistake**: Used `gcloud run services update` to fix a stale `DATA_STORE_ID` (caused by Terraform's `ignore_changes` workaround).
- **Chain**: Manual command cleared other env vars (`PROJECT_ID`, `LOCATION`) -> ETL failed with `projects/None` errors -> Restored via a second manual sync.
- **Prevention**: Avoid manual CLI updates when Terraform is managing the resource, or always use `--update-env-vars` instead of `--set-env-vars`.

### 4. CI/CD Variable Escaping
- **Problem**: Cloud Build failed because `$PYTHONPATH` was interpreted as a substitution.
- **Fix**: Escaped as `$$PYTHONPATH` in `cloudbuild.yaml`.

---

## 🛠 Skills Assessment
- **Used**: `gcp-architect` (Excellent for IAM/Service verification), `codebase_investigator`.
- **Useful**: `gcp-architect` was critical for diagnosing the BigQuery permission gaps.
- **Missed Opportunity**: Could have used `adk-dev-guide` earlier to ensure the `SequentialAgent` followed latest best practices for multi-agent handoffs.

---

## 🚀 How to build more seamlessly next time
1.  **Escape YAML early**: Always use `$$` for shell variables in `cloudbuild.yaml` from turn 1.
2.  **Model Availability**: Before hardcoding a model version, always perform a quick `curl` to `ListModels` to verify accessibility for that specific API key.
3.  **TF State Observability**: Add critical resource IDs (like `data_store_id`) to top-level Terraform outputs immediately to prevent "What is the bot actually using?" confusion.
4.  **Python Packaging**: Always include `__init__.py` in all subfolders if they are part of a CI/CD test run to avoid `ModuleNotFoundError`.
