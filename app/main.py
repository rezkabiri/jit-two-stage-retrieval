# app/main.py
import os
import uvicorn
from google.adk import App
from app.agent import root_agent

# Initialize the ADK App
# This happens at the package level when uvicorn loads the module
app = App(root_agent=root_agent, name="app")

if __name__ == "__main__":
    # Cloud Run provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting ADK Agent server on port {port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
