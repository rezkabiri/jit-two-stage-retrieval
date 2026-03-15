# app/main.py
import os
from fastapi import FastAPI
from google.adk import Agent, Model, App, tool

print("🚀 CONTAINER STARTING")

# 1. Bare minimum Tool
@tool
def starter_tool():
    return "System online."

# 2. Bare minimum Agent
# We use a lazy initialization for the Model if possible
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

print(f"🤖 Config: {PROJECT_ID} in {LOCATION}")

root_agent = Agent(
    name="two_stage_rag_agent",
    model=Model(
        name="gemini-3-flash-preview",
        project=PROJECT_ID,
        location=LOCATION,
    ),
    instruction="Hello! I am ready.",
    tools=[starter_tool],
)

# 3. Initialize ADK App
# We force in_memory to avoid any database hangs
adk_app = App(root_agent=root_agent, name="app", session_type="in_memory")

# 4. Expose the FastAPI instance directly for Uvicorn
app = adk_app.fastapi_app

@app.get("/health")
def health():
    return {"status": "ok", "message": "Container is listening"}

print("✅ Server initialization complete.")
