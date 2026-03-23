# app/agent.py
import os
from google.adk.agents import Agent, SequentialAgent
from app.tools.retriever import stage_1_retrieval
from app.reranker import rerank_documents

print("🚀 Initializing Agent module...")

# Configuration Switch: Vertex AI vs AI Studio
# Set USE_VERTEX_AI=true to use Vertex AI Model Garden (default for reliability)
# Set USE_VERTEX_AI=false to use AI Studio (Gemini API)
USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "true").lower() == "true"
AI_STUDIO_MODEL = os.getenv("AI_STUDIO_MODEL", "gemini-2.5-pro")
VERTEX_AI_MODEL = os.getenv("VERTEX_AI_MODEL", "gemini-2.5-pro")

if USE_VERTEX_AI:
    MODEL_NAME = VERTEX_AI_MODEL
    print(f"🔗 Model Backend: Vertex AI ({VERTEX_AI_MODEL}) | Project: {os.getenv('GOOGLE_CLOUD_PROJECT')} | Location: {os.getenv('GOOGLE_CLOUD_LOCATION')}")
else:
    MODEL_NAME = AI_STUDIO_MODEL
    print(f"🔗 Model Backend: AI Studio ({AI_STUDIO_MODEL})")


def create_rag_agent():
    return Agent(
        name="rag_agent",
        model=MODEL_NAME,
        instruction="""
        You are a highly-capable, two-stage RAG agent specializing in authorized document retrieval and grounded reasoning.
        
        ### Your Goal:
        Answer the user's query by retrieving documents, reranking them for maximum relevance, and providing a grounded response.
        
        ### Operational Workflow:
        1. **Retrieve**: Call `stage_1_retrieval` with the user's query and their authenticated email (found in the user context preamble if available).
        2. **Reason & Rerank**: If documents are found, pass the results to the `rerank_documents` tool to identify the top-scoring snippets.
        3. **Grounded Answer**: Analyze the reranked snippets and provide a precise, cited answer.
        
        ### Grounding & Safety Rules:
        - NEVER hypothesize or use outside knowledge. Only use information provided in the reranked snippets.
        - If no documents are found, or if none of the reranked documents contain the answer, state: "I'm sorry, I don't have enough information in the authorized documents to answer that question."
        - Prioritize information from the highest-scoring documents (rerank_score).
        
        ### Response Formatting:
        - Use Markdown for structured output (headers, lists, tables).
        - INCLUDE MANDATORY CITATIONS for every claim. Use the following format:
          > **Source:** [Title](Link)
          
        ### Citation Example:
        If the document title is "2025 Market Risk Report" and the link is "https://example.com/report1", the citation should be:
        > **Source:** [2025 Market Risk Report](https://example.com/report1)
        """,
        tools=[stage_1_retrieval, rerank_documents],
    )

# Use a single robust agent for the RAG journey
root_agent = create_rag_agent()

print("✅ Agent module initialized with unified RAG agent.")
