# app/tools/feedback.py
import os
import datetime
from typing import Optional, Dict, Any
from google.cloud import bigquery

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATASET_ID = os.getenv("FEEDBACK_DATASET_ID", "agent_feedback")
TABLE_ID = os.getenv("FEEDBACK_TABLE_ID", "user_feedback")

def record_feedback(
    message_id: str, 
    rating: str, 
    user_email: Optional[str] = None, 
    comment: Optional[str] = None
) -> str:
    """
    Records user feedback (thumbs up/down) for a specific agent response into BigQuery.
    """
    # ... existing implementation ...
    if not PROJECT_ID:
        return "Error: GOOGLE_CLOUD_PROJECT is not set."

    client = bigquery.Client()
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    # Schema: message_id (STRING), rating (STRING), user_email (STRING), 
    # comment (STRING), timestamp (TIMESTAMP)
    row_to_insert = [
        {
            "message_id": message_id,
            "rating": rating,
            "user_email": user_email or "anonymous",
            "comment": comment or "",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    ]

    try:
        errors = client.insert_rows_json(table_ref, row_to_insert)
        if errors == []:
            return f"Successfully recorded {rating} feedback for message {message_id}."
        else:
            return f"Error inserting feedback: {errors}"
    except Exception as e:
        return f"Failed to record feedback: {str(e)}"

def record_conversation(
    query: str, 
    response: str, 
    user_email: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Logs the full conversation trace to BigQuery for analytics and reranker training.
    
    Args:
        query: The user's input query.
        response: The agent's generated response.
        user_email: The identity of the user.
        metadata: Any additional context (e.g., latency, model name, retrieved doc IDs).
        
    Returns:
        A success or error message.
    """
    if not PROJECT_ID:
        return "Error: GOOGLE_CLOUD_PROJECT is not set."

    client = bigquery.Client()
    # Assuming a 'conversations' table in the same dataset
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.conversations"

    row_to_insert = [
        {
            "query": query,
            "response": response,
            "user_email": user_email,
            "metadata": str(metadata) if metadata else "{}",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    ]

    try:
        # We use insert_rows_json for simplicity, though for high volume, 
        # a streaming buffer or load job might be better.
        client.insert_rows_json(table_ref, row_to_insert)
        return "Conversation logged."
    except Exception as e:
        # Don't fail the main app flow if logging fails
        print(f"Failed to log conversation: {e}")
        return str(e)
