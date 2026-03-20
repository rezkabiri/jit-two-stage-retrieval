# App Core Tests

## Scope
This folder contains unit and integration tests for the Python FastAPI agent service and its supporting tools.

### Key Components Tested:
- **Agent Logic**: Verifying the SequentialAgent setup and instructions.
- **RBAC Mapping**: Ensuring `roles.py` correctly identifies user permissions based on emails.
- **Tool Integration**: Validating that the `retriever` and `feedback` tools construct requests correctly.
- **API Endpoints**: Testing `/api/chat`, `/api/feedback`, and `/health` using FastAPI TestClient.

## How to Run
Ensure you are in the `app/` directory and have dependencies installed:
```bash
cd app
pip install -r requirements.txt
pytest tests/
```

## Expectations
- All tests should pass with **100% mocked external services** (Vertex AI, BigQuery, Gemini API).
- No real network calls should be made during these tests.
- RBAC tests must fail explicitly if an unauthorized email attempts to access private roles.
