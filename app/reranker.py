# app/reranker.py
from typing import List, Dict, Any

class Reranker:
    def __init__(self, model_name: str = "mock"):
        """
        Mock Reranker that does not load heavy models.
        """
        print("💡 Using MOCK Reranker (no model loaded).")

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Returns the documents as is (already sorted by Stage 1).
        """
        return documents[:top_k]
