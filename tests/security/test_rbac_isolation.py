import pytest
from unittest.mock import MagicMock, patch
from app.tools.retriever import stage_1_retrieval

@pytest.fixture
def mock_search_client():
    with patch("app.tools.retriever.discoveryengine.SearchServiceClient") as mock_class:
        mock_instance = mock_class.return_value
        mock_instance.serving_config_path.return_value = "projects/test/locations/global/collections/default_collection/dataStores/test/servingConfigs/default_config"
        
        # Mock the search response
        mock_response = MagicMock()
        mock_response.results = []
        mock_instance.search.return_value = mock_response
        
        yield mock_instance

@patch("app.tools.retriever.PROJECT_ID", "test-project")
@patch("app.tools.retriever.DATA_STORE_ID", "test-datastore")
class TestRBACIsolation:
    """
    Security 'Red Team' tests to ensure RBAC filters are correctly applied 
    and prevent unauthorized data access.
    """

    def test_public_user_isolation(self, mock_search_client):
        """Verify that a public user ONLY sees 'public' documents."""
        stage_1_retrieval.func("query", user_email="stranger@gmail.com")
        
        args, _ = mock_search_client.search.call_args
        request = args[0]
        
        # Filter should only contain 'public'
        assert 'role: ANY("public")' in request.filter
        assert '"finance"' not in request.filter
        assert '"admin"' not in request.filter
        assert '"internal"' not in request.filter

    def test_finance_user_isolation(self, mock_search_client):
        """Verify that a finance user sees 'public' AND 'finance' documents."""
        stage_1_retrieval.func("query", user_email="analyst@finance.com")
        
        args, _ = mock_search_client.search.call_args
        request = args[0]
        
        # Filter should contain both 'public' and 'finance'
        assert 'role: ANY(' in request.filter
        assert '"public"' in request.filter
        assert '"finance"' in request.filter
        assert '"admin"' not in request.filter

    def test_admin_user_access(self, mock_search_client):
        """Verify that an admin user sees all authorized roles."""
        stage_1_retrieval.func("query", user_email="admin@bank.com")
        
        args, _ = mock_search_client.search.call_args
        request = args[0]
        
        # Admin should have a broad filter
        assert '"admin"' in request.filter
        assert '"finance"' in request.filter
        assert '"internal"' in request.filter
        assert '"public"' in request.filter

    def test_anonymous_user_isolation(self, mock_search_client):
        """Verify that missing identity defaults to 'public' only."""
        stage_1_retrieval.func("query", user_email=None)
        
        args, _ = mock_search_client.search.call_args
        request = args[0]
        
        assert request.filter == 'role: ANY("public")'

    def test_malicious_email_injection_prevention(self, mock_search_client):
        """
        Verify that identity is resolved via RoleManager and not 
        blindly trusted if someone tries to inject roles via email string.
        """
        # Attempting to inject a role in the email string
        stage_1_retrieval.func("query", user_email="user@gmail.com", "admin")
        
        args, _ = mock_search_client.search.call_args
        request = args[0]
        
        # The RoleManager should still map this unknown identity to just 'public'
        assert request.filter == 'role: ANY("public")'
        assert '"admin"' not in request.filter
