# app/reranker.py
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initializes the Cross-Encoder model.
        """
        import os
        cache_folder = os.getenv("SENTENCE_TRANSFORMERS_HOME")
        print(f"📦 Loading CrossEncoder from {cache_folder if cache_folder else 'default cache'}...")
        self.model = CrossEncoder(model_name)
        print("✅ CrossEncoder loaded successfully.")

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks a list of documents based on a query using a Cross-Encoder.
        
        Args:
            query: The user's query.
            documents: A list of document dicts (id, title, snippet, etc.).
            top_k: Number of top documents to return.
            
        Returns:
            A list of reranked documents, sorted by score.
        """
        if not documents:
            return []

        # Prepare pairs for the Cross-Encoder
        # The input format is [(query, doc1_text), (query, doc2_text), ...]
        pairs = [[query, doc.get("snippet", "")] for doc in documents]
        
        # Get relevance scores
        scores = self.model.predict(pairs)
        
        # Combine scores with documents and sort
        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])
            
        # Sort documents by score in descending order
        reranked_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        
        return reranked_docs[:top_k]
