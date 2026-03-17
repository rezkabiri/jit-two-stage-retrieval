# Local Development Setup

This directory contains scripts to quickly spin up the JIT Two-Stage Retrieval RAG application locally for development and testing.

## `setup_local.sh`

This script automates the initial setup for both the backend and frontend components.

### What it does:
1.  **Backend**: Creates a Python virtual environment in `app/.venv` and installs all dependencies from `requirements.txt`.
2.  **Frontend**: Installs Node.js dependencies in `frontend/node_modules`.
3.  **Vite Configuration**: Updates `frontend/vite.config.ts` to include a proxy that forwards `/api` requests to the backend (running on port 8080).

### How to use:

1.  **Run the setup script**:
    ```bash
    chmod +x scripts/local-dev/setup_local.sh
    ./scripts/local-dev/setup_local.sh
    ```

2.  **Start the Backend**:
    In a new terminal:
    ```bash
    cd app
    source .venv/bin/activate
    # Authenticate with GCP
    gcloud auth application-default login
    # Set required environment variables
    export GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
    export DATA_STORE_ID=rag-docs
    # Run the server
    python3 -m app.main
    ```

3.  **Start the Frontend**:
    In another terminal:
    ```bash
    cd frontend
    npm run dev
    ```

4.  **Access the UI**:
    Open your browser to `http://localhost:5173`.

### Port Forwarding (if on Cloudtop/Remote)
If you are running this on a remote instance, use SSH port forwarding to access the UI and backend:
```bash
ssh -L 5173:localhost:5173 -L 8080:localhost:8080 <your-instance-name>
```
