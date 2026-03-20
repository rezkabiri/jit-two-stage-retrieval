# tests/e2e/test_rbac_security.py
import pytest
from unittest.mock import MagicMock, patch
from app.tools.retriever import stage_1_retrieval

@pytest.fixture
def mock_search_client():
    with patch("app.tools.retriever.discoveryengine.SearchServiceClient") as mock:
        client_instance = mock.return_value
        # Mock a successful response
        mock_response = MagicMock()
        mock_response.results = []
        client_instance.search.return_value = mock_response
        yield client_instance

@patch("app.tools.retriever.PROJECT_ID", "test-project")
@patch("app.tools.retriever.DATA_STORE_ID", "test-ds")
def test_rbac_public_user(mock_search_client):
    """
    Test that a public user (no email) is restricted to 'public' documents.
    """
    stage_1_retrieval(query="some query")
    
    args, _ = mock_search_client.search.call_args
    request = args[0]
    
    assert 'role: ANY("public")' in request.filter

@patch("app.tools.retriever.PROJECT_ID", "test-project")
@patch("app.tools.retriever.DATA_STORE_ID", "test-ds")
def test_rbac_finance_user(mock_search_client):
    """
    Test that a finance user sees finance + public docs.
    """
    stage_1_retrieval(query="risk report", user_email="analyst@finance.com")
    
    args, _ = mock_search_client.search.call_args
    request = args[0]
    
    assert '"finance"' in request.filter
    assert '"public"' in request.filter

@patch("app.tools.retriever.PROJECT_ID", "test-project")
@patch("app.tools.retriever.DATA_STORE_ID", "test-ds")
def test_rbac_admin_user(mock_search_client):
    """
    Test that the admin user sees all roles.
    """
    stage_1_retrieval(query="everything", user_email="admin@rkabiri.altostrat.com")
    
    args, _ = mock_search_client.search.call_args
    request = args[0]
    
    for role in ["admin", "finance", "internal", "public"]:
        assert f'"{role}"' in request.filter
