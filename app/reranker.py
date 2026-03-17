# app/reranker.py
from typing import List, Dict, Any
from google.cloud import discoveryengine_v1beta as discoveryengine

class Reranker:
    def __init__(self, project_id: str, location: str = "global"):
        """
        Initialize the Vertex AI Ranking Service client.
        """
        self.project_id = project_id
        self.location = location
        
        if not project_id:
            print("⚠️ Reranker: PROJECT_ID not set. Reranking will be disabled.")
            self.client = None
            return

        print(f"🚀 Initializing Vertex AI Reranker for project: {project_id}")
        self.client = discoveryengine.RankServiceClient()
        self.ranking_config = self.client.ranking_config_path(
            project=project_id,
            location=location,
            ranking_config="default_ranking_config",
        )

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks the documents using the Vertex AI Ranking API (Cross-Encoder).
        """
        if not self.client or not documents:
            return documents[:top_k]
            
        try:
            # Map search results to RankingRecords
            records = [
                discoveryengine.RankingRecord(
                    id=str(i),
                    title=doc.get("title", ""),
                    content=doc.get("snippet", "")
                ) for i, doc in enumerate(documents)
            ]
            
            request = discoveryengine.RankRequest(
                ranking_config=self.ranking_config,
                model="semantic-ranker-52b", # Premium cross-encoder model
                top_n=top_k,
                query=query,
                records=records,
            )
            
            response = self.client.rank(request)
            
            # Map reranked records back to the original document structure
            reranked_docs = []
            for record in response.records:
                idx = int(record.id)
                doc = documents[idx].copy()
                doc["rerank_score"] = record.score
                reranked_docs.append(doc)
                
            return reranked_docs
            
        except Exception as e:
            print(f"❌ Reranking failed: {e}. Falling back to stage 1 results.")
            return documents[:top_k]
