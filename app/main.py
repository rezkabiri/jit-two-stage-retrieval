# app/main.py
import os
from fastapi import FastAPI
from .agent import root_agent

print("🚀 STARTING ADK AGENT SERVICE")

app = FastAPI()

# Mount the ADK agent under /api to match Load Balancer routing
root_agent.mount(app, path="/api")

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Use the PORT environment variable provided by Cloud Run
    port = int(os.environ.get("PORT", 8080))
    print(f"📡 Listening on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
