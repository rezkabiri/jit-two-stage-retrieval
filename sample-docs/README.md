# RBAC Testing Guide: Sample Documents

This directory contains curated sample documents used to validate the **Role-Based Access Control (RBAC)** logic of the JIT Two-Stage Retrieval Agent.

## Document Hierarchy & Access Levels

The ingestion pipeline (`data-pipeline/ingestion/parser.py`) automatically assigns RBAC roles based on the folder where the file is uploaded.

| Folder | Document | Assigned Role | Description |
| :--- | :--- | :--- | :--- |
| `public/` | `2025_global_economic_outlook.md` | `public` | Accessible to all users, including anonymous. |
| `finance/` | `2025_internal_market_risk.md` | `finance` | Restricted to Finance department members. |
| `private/admin/` | `Project_Phoenix_Acquisition.md` | `internal` | Highly confidential documents for internal/admin use. |

---

## User Personas for Testing

To test the security boundaries, you should simulate three distinct user personas. Identity is derived from the `X-Goog-Authenticated-User-Email` header provided by Identity-Aware Proxy (IAP).

### 1. The Public User
*   **Setup**: Use a personal Gmail account or a non-corporate email that isn't mapped in `app/roles.py`.
*   **Expected Behavior**:
    *   **Can answer**: "What is the global economic outlook for 2025?"
    *   **Should fail**: "What are our interest rate swap risks?" or "Tell me about Project Phoenix."
*   **Verification**: The bot should state it doesn't have information on the restricted topics.

### 2. The Finance Analyst
*   **Setup**: Use an email ending in `@finance.com` (e.g., `analyst@finance.com`).
*   **Expected Behavior**:
    *   **Can answer**: "What is the 2025 global outlook?" AND "What are the risks in our interest rate swap portfolio?"
    *   **Should fail**: "What is the status of Project Phoenix?"
*   **Verification**: The bot should provide specific details about the $50B portfolio and potential $400M loss.

### 3. The Executive Admin
*   **Setup**: Use the hardcoded admin email `admin@bank.com` or update `app/roles.py` to map your current user to the `internal` and `finance` roles.
*   **Expected Behavior**:
    *   **Can answer**: ALL queries including "Give me the details on Project Phoenix."
*   **Verification**: The bot should reveal the confidential acquisition of **NeoBank EU** for **$2.4 Billion**.

---

## How to Conduct the Test

1.  **Upload Documents**:
    Ensure the latest documents are in the ingestion bucket:
    ```bash
    gsutil -m cp -r sample-docs/* gs://[YOUR_INGESTION_BUCKET]/
    ```

2.  **Wait for Indexing**:
    Check the **Vertex AI Search Console** -> **Activity** tab. Ensure all 3 documents show a "Success" status.

3.  **Simulate Identity**:
    *   **In Production/Staging**: Authenticate via the Load Balancer using the relevant email.
    *   **In Local Dev**: You can mock the email in `app/main.py` or by setting a local environment variable if your setup supports it.

4.  **Verify Grounding**:
    Ask the bot for the **Source Citation** after each answer to ensure it is actually pulling from the correct restricted document.
