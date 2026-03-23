# ADR: Model Provider Flexibility (AI Studio vs. Vertex AI)

## Status
Accepted - 2026-03-20

## Context
Initial development was performed using **Google AI Studio (Gemini API)** due to its rapid prototyping capabilities and direct integration with the Google Agent Development Kit (ADK). However, as the project moved towards staging and production-level scale, several constraints emerged:
1.  **Quota Limitations**: The AI Studio Free Tier frequently encountered `429 RESOURCE_EXHAUSTED` errors during evaluation and multi-user testing.
2.  **Enterprise Reliability**: For high-availability RAG systems, the enterprise-grade quotas and SLAs provided by **Vertex AI** are necessary.
3.  **Model Evolution**: Foundation models (e.g., Gemini 1.5, 2.0, 2.5) evolve rapidly. Hardcoding model names or backends creates technical debt and prevents quick testing of new experimental versions.

## Decision
We decided to implement a **flexible model provider switch** (backend toggle) that allows the system to alternate between AI Studio and Vertex AI Model Garden at runtime. This is achieved through environment variables and a standardized model naming convention.

### Key Components:
1.  **`USE_VERTEX_AI` (Toggle)**: A boolean flag that determines the primary model backend. When `true`, the system routes requests to Vertex AI. When `false`, it defaults to AI Studio.
2.  **`VERTEX_AI_MODEL` / `AI_STUDIO_MODEL` (Configuration)**: Independent environment variables that specify which model to use for each provider. This allows us to point the system to a specific versioned model (e.g., `gemini-1.5-pro-002`) or an unversioned alias (e.g., `gemini-2.0-flash-001`).
3.  **Environment-Based Routing**: The backend switch is handled by the `GOOGLE_GENAI_USE_VERTEXAI` environment variable (recognized by the underlying SDK). This allows the application to use clean model identifiers (e.g., `gemini-2.0-flash-001`) while dynamically routing to the appropriate provider.

## Consequence
- **Resilience**: If a specific model or backend encounters quota exhaustion or availability issues, the operator can switch backends via a simple environment variable change without rebuilding the container.
- **Future-Proofing**: The system can point to experimental models (e.g., `gemini-2.5-pro`) immediately upon their availability in the Model Garden by simply updating the `VERTEX_AI_MODEL` variable.
- **Environment Parity**: Local developers can continue to use AI Studio for cost-free prototyping, while the CI/CD pipeline and Cloud Run services default to Vertex AI for production reliability.

## Implementation Details
- **Configuration Layer**: Controlled via Terraform in the `cloud_run` module.
- **Agent Layer**: Initialized in `app/agent.py` through dynamic `MODEL_NAME` construction.
- **Default Values**:
    - `USE_VERTEX_AI`: `true`
    - `VERTEX_AI_MODEL`: `gemini-2.0-flash-001`
    - `AI_STUDIO_MODEL`: `gemini-2.0-flash-001`
