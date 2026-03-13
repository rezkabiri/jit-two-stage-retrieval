# app/tools/retriever.py
import os
from typing import List, Optional
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.adk import tool

# Configuration (normally loaded from environment variables)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
DATA_STORE_ID = os.getenv("DATA_STORE_ID", "rag-docs")

@tool
def stage_1_retrieval(query: str, user_email: Optional[str] = None) -> List[dict]:
    """
    Performs the first stage retrieval from Vertex AI Search with RBAC filtering.
    
    Args:
        query: The user's search query.
        user_email: The authenticated user's email for RBAC filtering.
        
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

    # In a real app, we'd look up the user's role from a DB using their email.
    # For this scaffold, we'll simulate a role filter.
    # Vertex AI Search supports 'filter' in the SearchRequest.
    # Example filter: 'metadata.role: ANY("public", "finance")'
    
    role_filter = ""
    if user_email:
        # Placeholder: In production, map user_email to roles
        # roles = get_user_roles(user_email)
        # role_filter = f'role: ANY({", ".join([f""{r}"" for r in roles])})'
        role_filter = 'role: ANY("public")' # Default for now
    
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
            results.append({
                "id": doc.id,
                "title": doc.derived_struct_data.get("title", "Untitled"),
                "snippet": doc.derived_struct_data.get("snippets", [{}])[0].get("snippet", ""),
                "link": doc.derived_struct_data.get("link", ""),
                "metadata": dict(doc.struct_data)
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]
