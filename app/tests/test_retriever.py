# app/tests/test_retriever.py
import pytest
from unittest.mock import MagicMock, patch
from app.tools.retriever import stage_1_retrieval

@patch("app.tools.retriever.discoveryengine.SearchServiceClient")
@patch("app.tools.retriever.PROJECT_ID", "test-project")
@patch("app.tools.retriever.DATA_STORE_ID", "test-datastore")
def test_stage_1_retrieval_rbac_filter(mock_client_class):
    """Verify that the RBAC filter is correctly constructed in the search request."""
    mock_client = mock_client_class.return_value
    mock_client.serving_config_path.return_value = "mock-path"
    
    # Mock response
    mock_response = MagicMock()
    mock_response.results = []
    mock_client.search.return_value = mock_response

    # Test with a finance user - calling the underlying function
    stage_1_retrieval.func("what is the risk?", user_email="user@finance.com")

    # Inspect the call to search
    args, kwargs = mock_client.search.call_args
    request = args[0]
    
    assert 'role: ANY(' in request.filter
    assert '"finance"' in request.filter
    assert '"public"' in request.filter

def test_stage_1_retrieval_no_project():
    """Tool should return an error if PROJECT_ID is not set."""
    with patch("app.tools.retriever.PROJECT_ID", None):
        results = stage_1_retrieval.func("query")
        assert "error" in results[0]
        assert "GOOGLE_CLOUD_PROJECT is not set" in results[0]["error"]
