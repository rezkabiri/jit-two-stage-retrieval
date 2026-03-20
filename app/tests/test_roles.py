# app/tests/test_roles.py
import pytest
from app.roles import get_user_roles

def test_get_user_roles_anonymous():
    """Anonymous or None users should only have 'public' role."""
    assert get_user_roles(None) == ["public"]
    assert get_user_roles("anonymous") == ["public"]

def test_get_user_roles_domain_finance():
    """Users with finance.com domain should have 'finance' and 'public' roles."""
    roles = get_user_roles("user@finance.com")
    assert "finance" in roles
    assert "public" in roles
    assert len(roles) == 2

def test_get_user_roles_admin():
    """Specific admin emails should have multiple roles."""
    admin_email = "admin@rkabiri.altostrat.com"
    roles = get_user_roles(admin_email)
    assert "admin" in roles
    assert "finance" in roles
    assert "internal" in roles
    assert "public" in roles

def test_get_user_roles_unknown():
    """Unrecognized emails should default to 'public'."""
    roles = get_user_roles("stranger@other.com")
    assert roles == ["public"]
