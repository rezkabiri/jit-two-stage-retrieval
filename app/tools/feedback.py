# app/tools/feedback.py
import os
import datetime
from typing import Optional
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
    
    Args:
        message_id: The unique ID of the agent message being rated.
        rating: 'up' for thumbs up, 'down' for thumbs down.
        user_email: The email of the user providing feedback.
        comment: Optional text feedback from the user.
        
    Returns:
        A success or error message.
    """
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
