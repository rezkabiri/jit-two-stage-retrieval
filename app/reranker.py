# app/reranker.py
import os
import time
import datetime
import logging
from typing import List, Dict, Any
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.cloud import bigquery
from google.adk.tools import FunctionTool as tool

logger = logging.getLogger(__name__)

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

    def _log_error_to_bq(self, query: str, error: str):
        """Logs reranking errors to BigQuery for observability."""
        if not self.project_id:
            return
            
        try:
            bq_client = bigquery.Client(project=self.project_id)
            # Assuming the same dataset structure as other feedback tools
            dataset_id = os.getenv("FEEDBACK_DATASET_ID", "agent_feedback")
            table_id = "reranker_errors"
            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
            
            row_to_insert = [{
                "query": query,
                "error": str(error),
                "timestamp": datetime.datetime.utcnow().isoformat()
            }]
            
            bq_client.insert_rows_json(table_ref, row_to_insert)
        except Exception as bq_err:
            logger.error(f"Failed to log reranker error to BigQuery: {bq_err}")

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks the documents using the Vertex AI Ranking API (Cross-Encoder) with retries.
        """
        if not self.client or not documents:
            return documents[:top_k]
            
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

        max_retries = 3
        last_exception = None
        
        for attempt in range(max_retries):
            try:
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
                last_exception = e
                logger.warning(f"Reranking attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt # Exponential backoff: 1s, 2s
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Reranking failed after {max_retries} attempts. Falling back to stage 1 results.")
                    self._log_error_to_bq(query, e)
        
        return documents[:top_k]

# Global instance for tool use
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
_reranker_instance = Reranker(project_id=PROJECT_ID, location=LOCATION)

@tool
def rerank_documents(query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Reranks a list of retrieved document snippets using a semantic cross-encoder model.
    Use this to improve the relevance of results after an initial retrieval step.
    
    Args:
        query: The original search query.
        documents: A list of documents retrieved in Stage 1.
        top_k: The number of top reranked results to return.
        
    Returns:
        A reranked list of documents with semantic scores.
    """
    return _reranker_instance.rerank(query, documents, top_k)
