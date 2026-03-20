# End-to-End (E2E) System Tests

## Scope
This folder contains tests that validate the entire integrated system in a live environment (Staging).

### Key Components Tested:
- **Full Path Retrieval**: User -> Load Balancer -> IAP -> Cloud Run -> Vertex AI -> Cloud Run -> User.
- **RBAC Enforcement**: Verifying that different user emails receive different sets of documents based on their roles.
- **Feedback Persistence**: Ensuring that a "Thumbs Up" in the UI results in a new row in the `agent_feedback.user_feedback` BigQuery table.
- **Session Continuity**: Checking that conversation history is maintained for the user.

## How to Run
These tests require a live Staging environment and a valid user token (or service account with IAP access).
```bash
# Set your staging URL
export STAGING_URL="https://rag-stage.example.com"
export ID_TOKEN=$(gcloud auth print-identity-token)

cd tests/e2e
pytest test_rbac_security.py
```

## Expectations
- **Identity-based filtering**: A request from `admin@rkabiri.altostrat.com` MUST return documents from the `private/admin` folder.
- **Public-only fallback**: An anonymous or unrecognized user MUST NOT see any non-public documents.
- **Telemetry verification**: Integration tests for BigQuery should account for a 10-20 second streaming buffer delay.
