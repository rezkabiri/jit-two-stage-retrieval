# data-pipeline/tests/test_parser.py
import pytest
from ingestion.parser import map_rbac_roles

def test_map_rbac_roles_finance():
    """Verify that finance folders map to the finance role."""
    result = map_rbac_roles("finance/reports/2025_risk.md")
    assert result["role"] == "finance"
    assert result["folder"] == "finance"

def test_map_rbac_roles_private():
    """Verify that private folders map to the internal role."""
    result = map_rbac_roles("private/admin/secret_project.pdf")
    assert result["role"] == "internal"

def test_map_rbac_roles_public():
    """Verify that unknown or root folders default to the public role."""
    result = map_rbac_roles("public/news/intro.md")
    assert result["role"] == "public"
    
    result = map_rbac_roles("some_random_file.txt")
    assert result["role"] == "public"

def test_map_rbac_roles_source_path():
    """Verify that the source path is correctly formatted."""
    path = "legal/contracts/v1.pdf"
    result = map_rbac_roles(path)
    assert result["source_path"] == f"gs://{path}"
