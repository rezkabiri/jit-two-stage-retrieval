# app/agent.py
import os
from google.adk.agents import Agent, SequentialAgent
from app.tools.retriever import stage_1_retrieval
from app.reranker import rerank_documents

print("🚀 Initializing Agent module...")

# Configuration
MODEL_NAME = "gemini-3-flash-preview"

def create_retriever_agent():
    return Agent(
        name="retriever_agent",
        model=MODEL_NAME,
        instruction="""
        You are the first stage of a two-stage RAG pipeline.
        Your goal is to retrieve relevant documents from the knowledge base.
        
        1. Use the `stage_1_retrieval` tool to fetch raw documents.
        2. Pass the authenticated user's email if available for RBAC filtering.
        3. If you find documents, pass them as a structured list to the next stage.
        4. If no results are found, state that clearly.
        """,
        tools=[stage_1_retrieval],
    )

def create_reranker_agent():
    return Agent(
        name="reranker_agent",
        model=MODEL_NAME,
        instruction="""
        You are the second stage of a two-stage RAG pipeline.
        Your goal is to rerank the documents retrieved in the previous stage for maximum relevance.
        
        1. Use the `rerank_documents` tool on the documents retrieved by the retriever_agent.
        2. Analyze the reranked snippets and provide a precise, grounded answer to the user's question.
        3. Prioritize information from the highest-scoring documents.
        4. Include mandatory citations (titles and links) for all information used.
        5. Use markdown for clarity.
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
