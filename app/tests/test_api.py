
# app/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

def test_health_check():
    """Verify health endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("app.main.runner.run_async")
@patch("app.main.record_conversation")
def test_chat_endpoint(mock_record, mock_run_async):
    """Verify chat endpoint extracts user email and returns response."""
    # Mock runner events
    mock_event = MagicMock() # Use regular MagicMock for synchronous checks
    mock_event.is_final_response.return_value = True
    mock_event.content.parts = [MagicMock(text="Hello, I am an AI.")]
    
    async def mock_generator(*args, **kwargs):
        yield mock_event
        
    mock_run_async.return_value = mock_generator()

    headers = {"X-Goog-Authenticated-User-Email": "accounts.google.com:test@example.com"}
    response = client.post("/api/chat", json={"query": "hi"}, headers=headers)

    assert response.status_code == 200
    assert "response" in response.json()
    assert response.json()["response"] == "Hello, I am an AI."

@patch("app.main.record_feedback")
def test_feedback_endpoint(mock_record):
    """Verify feedback endpoint passes correct data to record_feedback."""
    mock_record.return_value = "Success"
    
    headers = {"X-Goog-Authenticated-User-Email": "test@example.com"}
    payload = {
        "messageId": "msg-123",
        "rating": "up",
        "comment": "Good job"
    }
    response = client.post("/api/feedback", json=payload, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_record.assert_called_once_with(
        message_id="msg-123",
        rating="up",
        user_email="test@example.com",
        comment="Good job"
    )
