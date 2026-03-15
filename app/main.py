# app/main.py
import os
import uvicorn
from google.adk import Agent, Model, App, tool

print("🚀 CONTAINER BOOT START")

# --- 1. Tools ---
@tool
def stage_1_retrieval(query: str, user_email: str = None) -> list:
    return [{"title": "Mock", "snippet": "Mock"}]

@tool
def record_feedback(message_id: str, rating: str, user_email: str = None) -> str:
    return "OK"

# --- 2. Agent ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "jit-tsr-rag-stage")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

print(f"🤖 Booting Agent in {PROJECT_ID}...")

root_agent = Agent(
    name="two_stage_rag_agent",
    model=Model(
        name="gemini-3-flash-preview",
        project=PROJECT_ID,
        location=LOCATION,
    ),
    instruction="Starter agent.",
    tools=[stage_1_retrieval, record_feedback],
)

# --- 3. App ---
# Force in_memory sessions to avoid Firestore dependencies during boot
app = App(root_agent=root_agent, name="app", session_type="in_memory")
print("✅ ADK App ready.")

if __name__ == "__main__":
    # Explicitly listen on 8080 (Cloud Run default)
    port = int(os.environ.get("PORT", 8080))
    print(f"📡 Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="debug")
