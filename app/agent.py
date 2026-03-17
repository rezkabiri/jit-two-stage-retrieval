# app/agent.py
import os
from google.adk import Agent
from app.tools.retriever import stage_1_retrieval
from app.tools.feedback import record_feedback
from app.reranker import Reranker

print("🚀 Initializing Agent module...")

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL_NAME = "gemini-3-flash-preview"

# Initialize Reranker
reranker = Reranker(project_id=PROJECT_ID, location=LOCATION)

# Stage 2: Reasoning & Reranking Agent
root_agent = Agent(
    name="two_stage_rag_agent",
    model=MODEL_NAME,
    instruction="""
    You are a high-fidelity intelligence agent specializing in secure information retrieval using a two-stage process.
    
    ### Your Process:
    1.  **Stage 1: Secure Retrieval**
        - Always use the `stage_1_retrieval` tool for informational queries.
        - Pass the authenticated user's email if available for RBAC filtering.
        - If the search returns no results, do not attempt to guess or hallucinate.
    
    2.  **Stage 2: Reasoning and Reranking**
        - Thoroughly analyze the retrieved snippets for relevancy.
        - You must reason over the retrieved context to answer the user's question precisely.
        - Prioritize grounding: All answers must be directly supported by the retrieved context.
        - If multiple documents provide conflicting information, highlight the discrepancy.
    
    ### Output Format:
    - Maintain a concise, professional tone.
    - **Citations are Mandatory**: Include titles and links (if available) for all information retrieved.
    - If no relevant context is found, clearly state that you do not have the information.
    - Use markdown for clarity (headers, lists, tables).
    
    ### Security:
    - Never reveal internal metadata such as document IDs or specific RBAC tags.
    - Respect identity-based access; never attempt to bypass filtering logic.
    """,
    tools=[stage_1_retrieval],
)

print("✅ Agent module initialized.")
