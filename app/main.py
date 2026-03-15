# app/main.py
import os
import sys
import uvicorn
from google.adk import Agent, Model, App, tool

print("🚀 CONTAINER STARTING...")

# --- 1. Tools ---
@tool
def stage_1_retrieval(query: str, user_email: str = None) -> list:
    """Mock retrieval tool."""
    print(f"🔍 Mock search for: {query}")
    return [{"title": "Mock Doc", "snippet": "This is a mock result for testing startup."}]

@tool
def record_feedback(message_id: str, rating: str, user_email: str = None) -> str:
    """Mock feedback tool."""
    return "Feedback recorded."

# --- 2. Agent ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

print(f"🤖 Initializing Agent (Project: {PROJECT_ID}, Location: {LOCATION})...")

root_agent = Agent(
    name="two_stage_rag_agent",
    model=Model(
        name="gemini-3-flash-preview",
        project=PROJECT_ID,
        location=LOCATION,
    ),
    instruction="You are a helpful RAG assistant. Use the tools provided.",
    tools=[stage_1_retrieval, record_feedback],
)

# --- 3. App ---
app = App(root_agent=root_agent, name="app")
print("✅ ADK App ready.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"📡 Starting uvicorn on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
