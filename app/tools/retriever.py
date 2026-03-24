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

# We use DATA_STORE_LOCATION for the retriever and GOOGLE_CLOUD_LOCATION for the LLM.
# If DATA_STORE_LOCATION is not set, we default to "global" for Vertex AI Search.
LOCATION = os.getenv("DATA_STORE_LOCATION", "global")
DATA_STORE_ID = os.getenv("DATA_STORE_ID")

# Resolve canonical location for the API endpoint (global, us, or eu)
# This handles mapping from regional (us-central1) to canonical (global/us/eu).
if LOCATION == "global":
    CANONICAL_LOCATION = "global"
elif LOCATION in ["us", "eu"]:
    CANONICAL_LOCATION = LOCATION
elif LOCATION.startswith("us-"):
    # If explicitly us-regional, we usually map to "us" multi-region endpoint,
    # UNLESS the datastore was created in "global".
    # In this project, infrastructure/modules/vertex_ai/main.tf uses "global".
    CANONICAL_LOCATION = "us" 
elif LOCATION.startswith("eu-"):
    CANONICAL_LOCATION = "eu"
else:
    CANONICAL_LOCATION = "global"

# Override: If the Data Store is known to be global (as in this infra), force global.
if os.getenv("DATA_STORE_LOCATION") == "global":
    CANONICAL_LOCATION = "global"

@tool
def stage_1_retrieval(query: str, user_email: Optional[str] = None) -> List[dict]:
    """
    Performs the first stage retrieval from Vertex AI Search with RBAC filtering.
    """
    if not PROJECT_ID:
        return [{"error": "GOOGLE_CLOUD_PROJECT is not set."}]

    # Resolve the correct API endpoint based on canonical location
    endpoint = "discoveryengine.googleapis.com"
    if CANONICAL_LOCATION in ["us", "eu"]:
        endpoint = f"{CANONICAL_LOCATION}-discoveryengine.googleapis.com"
    
    client_options = {"api_endpoint": endpoint}
    client = discoveryengine.SearchServiceClient(client_options=client_options)
    
    # Define the serving config path
    serving_config = client.serving_config_path(
        project=PROJECT_ID,
        location=CANONICAL_LOCATION,
        data_store=DATA_STORE_ID,
        serving_config="default_config",
    )

    logger.info(f"📡 Using Discovery Engine Endpoint: {endpoint} | Resource Location: {CANONICAL_LOCATION}")

    # Resolve roles for RBAC filtering
    roles = get_user_roles(user_email)
    role_list = ", ".join([f'"{r}"' for r in roles])
    role_filter = f"role: ANY({role_list})"
    
    # Stage 1: Initial Retrieval
    # NOTE: We avoid extractive_content_spec because it requires Enterprise Edition.
    # snippet_spec is available in Standard Edition.
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
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
        logger.info(f"🔍 Stage 1 Retrieval: Found {len(response.results)} candidates for query: '{query}'")
        
        for result in response.results:
            doc = result.document
            derived = doc.derived_struct_data or {}
            
            # Extract content from snippets (Standard Edition)
            snippet = ""
            snippets = derived.get("snippets", [])
            if snippets:
                snippet = snippets[0].get("snippet", "")
            
            if not snippet and doc.struct_data:
                # Fallback to struct data content if available
                snippet = doc.struct_data.get("content", "")[:500]

            logger.info(f"  - Doc ID: {doc.id} | Title: {derived.get('title', 'Untitled')}")

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
