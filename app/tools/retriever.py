# app/tools/retriever.py
import os
from typing import List, Optional
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.adk.tools import FunctionTool as tool
from app.roles import get_user_roles

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
        print(f"🔍 Stage 1 Retrieval: Found {len(response.results)} candidates for query: '{query}' with filter: '{role_filter}'")
        
        for result in response.results:
            doc = result.document
            derived = doc.derived_struct_data or {}
            
            # ... (rest of the extraction logic)
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

            print(f"  - Doc ID: {doc.id} | Title: {derived.get('title', 'Untitled')} | Snippet Length: {len(snippet)}")

            results.append({
                "id": doc.id,
                "title": derived.get("title", doc.struct_data.get("title", "Untitled")),
                "snippet": snippet,
                "link": derived.get("link", doc.struct_data.get("source_path", "")),
                "metadata": dict(doc.struct_data) if doc.struct_data else {}
            })
            
        return results
    except Exception as e:
        print(f"❌ Retrieval tool error: {e}")
        return [{"error": str(e)}]
