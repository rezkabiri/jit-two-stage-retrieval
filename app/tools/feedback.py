# app/tools/feedback.py
import os
import logging
import datetime
from typing import Optional, Dict, Any
from google.cloud import bigquery

# Configure logging
logger = logging.getLogger(__name__)

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
    logger.info(f"💾 Recording feedback: {rating} for message {message_id} (User: {user_email})")
    
    if not PROJECT_ID:
        logger.error("❌ GOOGLE_CLOUD_PROJECT is not set.")
        return "Error: GOOGLE_CLOUD_PROJECT is not set."

    client = bigquery.Client()
    # ...
    # ...
    try:
        errors = client.insert_rows_json(table_ref, row_to_insert)
        if errors == []:
            msg = f"✅ Successfully recorded {rating} feedback for message {message_id}."
            logger.info(msg)
            return msg
        else:
            logger.error(f"❌ Error inserting feedback: {errors}")
            return f"Error inserting feedback: {errors}"
    except Exception as e:
        logger.error(f"❌ Failed to record feedback: {e}", exc_info=True)
        return f"Failed to record feedback: {str(e)}"

def record_conversation(
    query: str, 
    response: str, 
    user_email: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Logs the full conversation trace to BigQuery for analytics and reranker training.
    """
    logger.info(f"📜 Logging conversation trace for user: {user_email}")
    
    if not PROJECT_ID:
        logger.error("❌ GOOGLE_CLOUD_PROJECT is not set.")
        return "Error: GOOGLE_CLOUD_PROJECT is not set."

    client = bigquery.Client()
    # ...
    # ...
    try:
        # We use insert_rows_json for simplicity, though for high volume, 
        # a streaming buffer or load job might be better.
        client.insert_rows_json(table_ref, row_to_insert)
        logger.info(f"✅ Conversation trace logged successfully.")
        return "Conversation logged."
    except Exception as e:
        # Don't fail the main app flow if logging fails
        logger.error(f"❌ Failed to log conversation trace: {e}", exc_info=True)
        return str(e)
