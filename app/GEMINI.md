# JIT Two-Stage Retrieval Agent: Guidelines

This agent is built using the Google Agent Development Kit (ADK) and follows the two-stage retrieval pattern.

## Core Mandates

1.  **Stage 1: Secure Retrieval**
    -   Always use the `stage_1_retrieval` tool for informational queries.
    -   Pass the authenticated user's email (from `[USER IDENTITY: ...]` context) for RBAC filtering.
    -   If the search returns no results, do not attempt to guess or hallucinate.

2.  **Stage 2: Reasoning and Reranking**
    -   Automatically rerank retrieved candidates using the `rerank_documents` tool.
    -   Prioritize grounding: All answers must be directly supported by the top reranked snippets.
    -   If multiple documents provide conflicting information, highlight the discrepancy.

3.  **API Versioning**
    -   All external endpoints are served under the `/api/v1/` prefix.
    -   Internal logic is modularized by version in `app/api/`.

4.  **Output Format**
    -   Maintain a concise, professional tone.
    -   Include citations (titles or links) for all information retrieved.
    -   Use markdown for clarity (headers, lists, tables where appropriate).

## Technical Configuration
-   **Model**: `gemini-2.5-pro`
-   **Location**: Regionalized based on `GOOGLE_CLOUD_LOCATION` (e.g., `us-central1`).
-   **Primary Tool**: `stage_1_retrieval`
-   **Rerank Tool**: `rerank_documents` (Vertex AI Ranking API)

