# Ingestion Pipeline Tests

## Scope
This folder contains tests for the Document Ingestion ETL pipeline (Cloud Function).

### Key Components Tested:
- **Markdown Parser**: Ensuring that roles (`internal`, `finance`, etc.) are correctly extracted from file paths.
- **Metadata Extraction**: Verifying that the document ID and display name are generated correctly.
- **Cloud Function Trigger**: Simulating a GCS event to verify the processing flow.

## How to Run
Ensure you are in the `data-pipeline/ingestion` directory:
```bash
cd data-pipeline/ingestion
pip install -r requirements.txt
pytest ../tests/
```

## Expectations
- The parser must correctly identify the role based on the directory structure (e.g., `finance/` -> `finance`).
- If a file is uploaded to an unrecognized directory, it should default to `public` or log a warning.
- All external dependencies (GCS, Vertex AI) must be mocked.
