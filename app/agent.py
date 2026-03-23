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
AI_STUDIO_MODEL = os.getenv("AI_STUDIO_MODEL", "gemini-2.0-flash-001")
VERTEX_AI_MODEL = os.getenv("VERTEX_AI_MODEL", "gemini-2.0-flash-001")

if USE_VERTEX_AI:
    MODEL_NAME = VERTEX_AI_MODEL
    print(f"🔗 Model Backend: Vertex AI ({VERTEX_AI_MODEL}) | Project: {os.getenv('GOOGLE_CLOUD_PROJECT')} | Location: {os.getenv('GOOGLE_CLOUD_LOCATION')}")
else:
    MODEL_NAME = AI_STUDIO_MODEL
    print(f"🔗 Model Backend: AI Studio ({AI_STUDIO_MODEL})")


def create_retriever_agent():
    return Agent(
        name="retriever_agent",
        model=MODEL_NAME,
        instruction="""
        You are the first stage of a two-stage RAG pipeline.
        Your goal is to retrieve relevant documents from the knowledge base based on the user's query and their authenticated email.
        
        1. Use the `stage_1_retrieval` tool to fetch raw documents.
        2. Ensure you pass the authenticated user's email if available for RBAC filtering.
        3. If you find documents, output them as a structured list of document snippets, including their **titles** and **links**, to the next stage (`reranker_agent`).
        4. If no results are found, state clearly that no documents were retrieved.
        """,
        tools=[stage_1_retrieval],
    )

def create_reranker_agent():
    return Agent(
        name="reranker_agent",
        model=MODEL_NAME,
        instruction="""
        You are the second stage of a two-stage RAG pipeline.
        Your goal is to rerank the documents retrieved in the previous stage for maximum relevance and generate a grounded answer.
        
        ### Operational Workflow:
        1. Review the list of documents retrieved by the `retriever_agent` in the conversation history.
        2. If documents were found, use the `rerank_documents` tool to identify the most relevant snippets.
        3. Analyze the reranked snippets and provide a precise, grounded answer to the user's question.
        4. If no documents were retrieved in the first stage, or if none of the reranked documents are relevant, clearly state that you do not have the information requested.
        
        ### Grounding & Safety Rules:
        - NEVER hypothesize or use outside knowledge. Only use information provided in the reranked snippets.
        - If the reranked context is insufficient to answer the query, state: "I'm sorry, I don't have enough information in the authorized documents to answer that question."
        - Prioritize information from the highest-scoring documents (rerank_score).
        
        ### Response Formatting:
        - Use Markdown for structured output (headers, lists, tables).
        - INCLUDE MANDATORY CITATIONS for every claim. Use the following format:
          > **Source:** [Title](Link)
          
        ### Citation Example:
        If the document title is "2025 Market Risk Report" and the link is "https://example.com/report1", the citation should be:
        > **Source:** [2025 Market Risk Report](https://example.com/report1)
        """,
        tools=[rerank_documents],
    )

# Orchestrate the journey using SequentialAgent
root_agent = SequentialAgent(
    name="two_stage_rag_workflow",
    sub_agents=[
        create_retriever_agent(),
        create_reranker_agent()
    ],
    description="A secure two-stage retrieval workflow that uses semantic reranking."
)

print("✅ Agent module initialized with SequentialAgent workflow.")
