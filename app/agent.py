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
        Your goal is to retrieve relevant documents from the knowledge base based on the user's query and their authenticated email.
        
        1. Use the `stage_1_retrieval` tool to fetch raw documents.
        2. Ensure you pass the authenticated user's email if available for RBAC filtering.
        3. If you find documents, output them as a structured list of document snippets to the next stage (`reranker_agent`).
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
        
        1. Review the list of documents retrieved by the `retriever_agent` in the conversation history.
        2. If documents were found, use the `rerank_documents` tool to identify the most relevant snippets.
        3. Analyze the reranked snippets and provide a precise, grounded answer to the user's question.
        4. If no documents were retrieved in the first stage, or if none of the reranked documents are relevant, clearly state that you do not have the information requested.
        5. Prioritize information from the highest-scoring documents.
        6. Include mandatory citations (titles and links) for all information used.
        7. Use markdown for clarity.
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
