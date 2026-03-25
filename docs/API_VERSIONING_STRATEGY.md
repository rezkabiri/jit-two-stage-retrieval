# API Versioning Strategy

This document outlines the architectural decision for versioning the JIT Two-Stage Retrieval RAG API.

## Versioning Options Considered

| Option | Strategy | Description | Pros | Cons |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Path-Based** | Version in URL: `/api/v1/chat` | **Highly observable**, easy to cache, compatible with all LBs. | Requires client URL updates for major changes. |
| **2** | **Header-Based** | Custom Header: `X-API-Version: 1` | Clean URLs, allows client opt-in without path changes. | Harder to debug in logs/browsers, complex internal routing. |
| **3** | **Accept Header** | Media Type: `Accept: application/vnd.rag.v1+json` | RESTfully correct, follows standard content negotiation. | High overhead to implement, often overkill for internal tools. |
| **4** | **Parameter-Based** | Query Param: `/api/chat?v=1` | Simple to implement and test via browser. | Can conflict with caching logic, less standard for REST. |

---

## The Chosen Strategy: Option 1 (Path-Based)

We have chosen **Path-Based Versioning** (e.g., `/api/v1/chat`) as the standard for this project.

### Why we chose this:
1.  **Observability & Traceability**: Looking at Cloud Run or Load Balancer logs immediately tells us which version of the logic is being hit without inspecting headers.
2.  **Infrastructure Compatibility**: GCP Global Load Balancers can easily route requests based on path prefixes. This allows us to perform **Canary Deployments** or route `v2` traffic to an entirely different backend service if needed.
3.  **Documentation (Swagger) Isolation**: FastAPI makes it trivial to host separate OpenAPI schemas for different versions (e.g., `/api/v1/docs` vs `/api/v2/docs`), keeping the developer experience clean.
4.  **Simplicity**: It follows the principle of "explicit over implicit." Developers and automated tools can immediately see the contract version they are interacting with.

---

## Implementation Details

### Directory Structure
The application logic is organized by version to prevent "spaghetti code":
```text
app/
├── main.py              # Root app, includes versioned routers
└── api/
    └── v1/
        ├── router.py    # Aggregate router for v1
        └── endpoints/   # Functional logic for v1 (chat, feedback)
```

### Adding a New Version (v2)
To introduce a breaking change:
1.  Create a new folder `app/api/v2/`.
2.  Define new logic in `app/api/v2/endpoints/`.
3.  Register the new router in `app/main.py`:
    ```python
    from app.api.v2.router import api_router as v2_router
    app.include_router(v2_router, prefix="/api/v2")
    ```
4.  Update the frontend to point to the new endpoints at its own pace.
