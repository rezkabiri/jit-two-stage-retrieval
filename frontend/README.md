# JIT Two-Stage RAG: React Frontend

A sleek, minimal chat interface for the JIT Two-Stage Retrieval Agentic RAG system.

## Features
- **Modern Chat UI**: Clean, responsive design with dark/light mode support.
- **IAP Ready**: Designed to work behind Google Cloud's Identity-Aware Proxy.
- **Real-time Feedback**: Integrated thumbs up/down buttons for agent response evaluation.
- **Markdown Support**: (Planned) Rendering for rich agent responses.
- **Citations**: Clear display of document sources and timestamps.

## Prerequisites
- **Node.js**: v18+
- **npm**: v9+

## Development

1.  **Install Dependencies**:
    ```bash
    cd frontend
    npm install
    ```

2.  **Run Dev Server**:
    ```bash
    npm run dev
    ```

## Production Build

1.  **Build Assets**:
    ```bash
    npm run build
    ```
2.  The optimized assets will be in the `dist/` directory, ready to be served by a web server or a Cloud Run service.

## API Integration
The frontend expects two main API endpoints (proxied to the ADK backend):
- `POST /api/chat`: Sends a query to the agent.
- `POST /api/feedback`: Logs user feedback (thumbs up/down) to BigQuery.
