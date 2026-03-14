# app/main.py
import os
import uvicorn
from google.adk import App

# Use absolute imports to ensure package consistency
from app.agent import root_agent

# Create the ADK App
# The name MUST match the package name "app"
app = App(root_agent=root_agent, name="app")

if __name__ == "__main__":
    # Cloud Run provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    # Run the server directly using the app object
    print(f"🚀 Starting JIT RAG Agent on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
