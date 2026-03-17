# app/tools/retriever.py
import os
from typing import List, Optional
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.adk.tools import FunctionTool as tool

# Configuration (normally loaded from environment variables)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
DATA_STORE_ID = os.getenv("DATA_STORE_ID", "rag-docs")

def get_user_roles(user_email: Optional[str]) -> List[str]:
    """
    Mock role mapping logic. In production, this would query a database or IAM service.
    """
    if not user_email or user_email == "anonymous":
        return ["public"]
    
    roles = ["public"]
    if user_email.endswith("@finance.com") or user_email == "admin@bank.com":
        roles.append("finance")
    if user_email.endswith("@legal.com"):
        roles.append("legal")
    
    return roles

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
