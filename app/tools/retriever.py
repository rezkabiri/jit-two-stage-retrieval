# app/tools/retriever.py
import os
from typing import List, Optional
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.adk.tools import FunctionTool as tool
from app.roles import get_user_roles

# Configuration (normally loaded from environment variables)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
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

    client = discoveryengine.SearchServiceClient()
    
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
    
    # Stage 1: Initial Retrieval
    search_request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=10, 
        filter=role_filter,
    )

    try:
        response = client.search(search_request)
        results = []
        for result in response.results:
            doc = result.document
            derived = doc.derived_struct_data or {}
            results.append({
                "id": doc.id,
                "title": derived.get("title", "Untitled"),
                "snippet": derived.get("snippets", [{}])[0].get("snippet", "") if derived.get("snippets") else "",
                "link": derived.get("link", ""),
                "metadata": dict(doc.struct_data) if doc.struct_data else {}
            })
            
        return results
    except Exception as e:
        print(f"❌ Retrieval tool error: {e}")
        return [{"error": str(e)}]
