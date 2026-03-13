# E2E Security & RBAC Testing

This directory contains functional tests designed to verify the security boundaries of the JIT Two-Stage Retrieval system.

## The "Red Team" Strategy
Because security is the core value of this architecture, we use automated "Red Team" tests to attempt to bypass RBAC filters. We mock the underlying Vertex AI Search (Discovery Engine) responses to focus specifically on whether our **filter injection logic** is correct.

## What is Tested?
- **Identity Extraction**: Ensuring the `X-Goog-Authenticated-User-Email` (simulated in session state) is correctly captured.
- **Filter Construction**: Verifying that the `stage_1_retrieval` tool builds the correct `discoveryengine.SearchRequest` filter string (e.g., `role: ANY("finance")`).
- **Default Deny**: Confirming that requests without a valid identity default to `role: ANY("public")`.

## How to Run
From the root:
```bash
pytest tests/e2e/
```
