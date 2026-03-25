import os
import logging

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# --- CRITICAL: Vertex AI Environment Setup ---
# This MUST happen before any google.adk or google.genai imports to ensure the SDK
# picks up the correct backend and regional location.
USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "true").lower() == "true"
if USE_VERTEX_AI:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    # Force a regional location for the LLM. 
    llm_location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    if llm_location == "global":
        llm_location = "us-central1"
    os.environ["GOOGLE_CLOUD_LOCATION"] = llm_location
    
    # Remove API Key to prevent defaulting to AI Studio
    if "GOOGLE_API_KEY" in os.environ:
        del os.environ["GOOGLE_API_KEY"]
    
    logger.info(f"🔗 Global Setup: Vertex AI mode enabled. Location: {llm_location}")

from fastapi import FastAPI
from app.api.v1.router import api_router as v1_router

logger.info("🚀 STARTING AGENT SERVICE")

app = FastAPI(
    title="JIT Two-Stage Retrieval RAG API",
    description="Production-grade Agentic RAG solution on GCP",
    version="1.0.0"
)

# Include versioned routers
app.include_router(v1_router, prefix="/api/v1")

@app.get("/health")
def health():
    """Version-independent health check"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
