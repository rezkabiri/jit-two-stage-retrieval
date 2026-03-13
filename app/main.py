# app/main.py
import os
import uvicorn
from google.adk import App
from .agent import root_agent

# Create the ADK App
# The name MUST match the directory name "app" for some ADK internal routing
app = App(root_agent=root_agent, name="app")

if __name__ == "__main__":
    # Cloud Run provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=port)
