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
        
        # Use DATA_STORE_LOCATION or default to "global" for Vertex Ranking API
        self.location = os.getenv("DATA_STORE_LOCATION", "global")
        
        if not project_id:
            logger.warning("⚠️ Reranker: PROJECT_ID not set. Reranking will be disabled.")
            self.client = None
            return

        logger.info(f"🚀 Initializing Vertex AI Reranker for project: {project_id}")
        
        # Resolve canonical location for the API endpoint (global, us, or eu)
        if self.location == "global":
            canonical_location = "global"
        elif self.location in ["us", "eu"]:
            canonical_location = self.location
        elif self.location.startswith("us-"):
            canonical_location = "us"
        elif self.location.startswith("eu-"):
            canonical_location = "eu"
        else:
            canonical_location = "global"

        endpoint = "discoveryengine.googleapis.com"
        if canonical_location in ["us", "eu"]:
            endpoint = f"{canonical_location}-discoveryengine.googleapis.com"
            
        logger.info(f"📡 Using Rank API Endpoint: {endpoint} | Resource Location: {canonical_location}")

        self.client = discoveryengine.RankServiceClient(client_options={"api_endpoint": endpoint})
        self.ranking_config = self.client.ranking_config_path(
            project=project_id,
            location=canonical_location,
            ranking_config="default_ranking_config",
        )

    def _log_error_to_bq(self, query: str, error: str):
        """Logs reranking errors to BigQuery for observability."""
        if not self.project_id:
            return
            
        try:
            bq_client = bigquery.Client(project=self.project_id)
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
            
        records = [
            discoveryengine.RankingRecord(
                id=str(i),
                title=doc.get("title", ""),
                content=doc.get("snippet", "")
            ) for i, doc in enumerate(documents)
        ]
        
        request = discoveryengine.RankRequest(
            ranking_config=self.ranking_config,
            model="semantic-ranker-52b",
            top_n=top_k,
            query=query,
            records=records,
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.rank(request)
                reranked_docs = []
                for record in response.records:
                    idx = int(record.id)
                    doc = documents[idx].copy()
                    doc["rerank_score"] = record.score
                    reranked_docs.append(doc)
                return reranked_docs
            except Exception as e:
                logger.warning(f"Reranking attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"❌ Reranking failed after {max_retries} attempts.")
                    self._log_error_to_bq(query, e)
        return documents[:top_k]

# Global instance for tool use
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
# Data Store location is typically "global"
LOCATION = os.getenv("DATA_STORE_LOCATION", "global")
_reranker_instance = Reranker(project_id=PROJECT_ID, location=LOCATION)

@tool
def rerank_documents(query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Reranks a list of retrieved document snippets using a semantic cross-encoder model.
    """
    return _reranker_instance.rerank(query, documents, top_k)
