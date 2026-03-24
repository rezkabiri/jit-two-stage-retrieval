# app/tools/retriever.py
import os
import logging
from typing import List, Optional
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.adk.tools import FunctionTool as tool
from app.roles import get_user_roles

logger = logging.getLogger(__name__)

# Configuration (normally loaded from environment variables)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
# Data Store location is typically "global", while Gemini models are regional.
# We use DATA_STORE_LOCATION for the retriever and GOOGLE_CLOUD_LOCATION for the LLM.
LOCATION = os.getenv("DATA_STORE_LOCATION") or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
DATA_STORE_ID = os.getenv("DATA_STORE_ID")

@tool
def stage_1_retrieval(query: str, user_email: Optional[str] = None) -> List[dict]:
    """
    Performs the first stage retrieval from Vertex AI Search with RBAC filtering.
    Always call this first when information is needed from the knowledge base.
    
    Args:
        query: The user's search query.
        user_email: The authenticated user's email for RBAC filtering (optional).
        
    Returns:
        A list of retrieved document snippets and their metadata.
    """
    if not PROJECT_ID:
        return [{"error": "GOOGLE_CLOUD_PROJECT is not set."}]

    # Resolve the correct API endpoint based on location
    # Valid endpoints are discoveryengine.googleapis.com (global), 
    # us-discoveryengine.googleapis.com, or eu-discoveryengine.googleapis.com.
    client_options = None
    if LOCATION in ["us", "eu"]:
        client_options = {"api_endpoint": f"{LOCATION}-discoveryengine.googleapis.com"}
    elif LOCATION != "global":
        # If a specific region like us-central1 is provided, we often still need 
        # to use the 'global' or 'us'/'eu' multi-region endpoint for the API.
        # Since our data store is 'global', we default to global.
        client_options = {"api_endpoint": "discoveryengine.googleapis.com"}
    
    client = discoveryengine.SearchServiceClient(client_options=client_options)
    
    # Define the serving config path
    serving_config = client.serving_config_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        serving_config="default_config",
    )

    # Resolve roles for RBAC filtering
    roles = get_user_roles(user_email)
    role_list = ", ".join([f'"{r}"' for r in roles])
    role_filter = f"role: ANY({role_list})"
    
    # Stage 1: Initial Retrieval with Content Search Spec for better snippets
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
            max_extractive_answer_count=1
        )
    )

    search_request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=10, 
        filter=role_filter,
        content_search_spec=content_search_spec,
    )

    try:
        response = client.search(search_request)
        results = []
        logger.info(f"🔍 Stage 1 Retrieval: Found {len(response.results)} candidates for query: '{query}' with filter: '{role_filter}'")
        
        for result in response.results:
            doc = result.document
            derived = doc.derived_struct_data or {}
            
            # Extract content from various sources
            snippet = ""
            extractive_answers = derived.get("extractive_answers", [])
            if extractive_answers:
                snippet = extractive_answers[0].get("content", "")
            
            if not snippet:
                snippets = derived.get("snippets", [])
                if snippets:
                    snippet = snippets[0].get("snippet", "")
            
            if not snippet and doc.struct_data:
                snippet = doc.struct_data.get("content", "")[:500]

            logger.info(f"  - Doc ID: {doc.id} | Title: {derived.get('title', 'Untitled')} | Snippet Length: {len(snippet)}")

            results.append({
                "id": doc.id,
                "title": derived.get("title", doc.struct_data.get("title", "Untitled")),
                "snippet": snippet,
                "link": derived.get("link", doc.struct_data.get("source_path", "")),
                "metadata": dict(doc.struct_data) if doc.struct_data else {}
            })
            
        return results
    except Exception as e:
        logger.error(f"❌ Retrieval tool error: {e}", exc_info=True)
        return [{"error": str(e)}]
