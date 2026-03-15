# app/agent.py
import os
from google.adk import Agent, Model
from app.tools.retriever import stage_1_retrieval
from app.tools.feedback import record_feedback

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL_NAME = "gemini-3-flash-preview"

# We will lazy-load the reranker to speed up startup
_reranker_instance = None

def get_reranker():
    global _reranker_instance
    if _reranker_instance is None:
        from app.reranker import Reranker
        print("📡 Lazy-loading Reranker model...")
        _reranker_instance = Reranker()
    return _reranker_instance

# Stage 2: Reasoning & Reranking Agent
root_agent = Agent(
    name="two_stage_rag_agent",
    model=Model(
        name=MODEL_NAME,
        project=PROJECT_ID,
        location=LOCATION,
    ),
    instruction="""
    You are a high-fidelity intelligence agent specializing in secure information retrieval.
    You operate in a two-stage retrieval process:
    1.  **Stage 1 (Retrieval)**: Use the `stage_1_retrieval` tool to fetch documents based on the user's query and their authenticated email.
    2.  **Stage 2 (Reasoning & Reranking)**: Carefully analyze the retrieved documents. 
        -   **Refinement**: Filter out irrelevant or lower-quality snippets.
        -   **Grounding**: Ensure the final answer is directly supported by the most relevant context.
        -   **Precision**: Prioritize documents with higher semantic relevance.
    
    **Instructions**:
    -   Always use the `stage_1_retrieval` tool for any informational query.
    -   Extract the user's email from the session context (if available).
    -   Cite your sources clearly using the document title or link provided.
    -   If no relevant information is found, state that you do not have the answer. Do not hallucinate.
    -   Maintain a professional and precise tone.
    """,
    tools=[stage_1_retrieval, record_feedback],
)
