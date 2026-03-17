# app/agent.py
import os
from google.adk import Agent
from .tools.retriever import stage_1_retrieval
from .tools.feedback import record_feedback
from .reranker import Reranker

print("🚀 Initializing Agent module...")

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL_NAME = "gemini-3-flash-preview"

# Initialize Reranker (currently mocked for stability)
reranker = Reranker()

# Stage 2: Reasoning & Reranking Agent
root_agent = Agent(
    name="two_stage_rag_agent",
    model=MODEL_NAME,
    instruction="""
    You are a high-fidelity intelligence agent specializing in secure information retrieval.
    You operate in a two-stage retrieval process:
    1.  **Stage 1 (Retrieval)**: Use the `stage_1_retrieval` tool to fetch documents.
    2.  **Stage 2 (Reasoning & Reranking)**: Carefully analyze the retrieved documents. 
    """,
    tools=[stage_1_retrieval, record_feedback],
)

print("✅ Agent module initialized.")
