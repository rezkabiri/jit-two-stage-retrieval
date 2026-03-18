# app/roles.py
import os
import json
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class RoleManager:
    """
    Handles role mapping for users based on their identity.
    Can be configured via a JSON file or environment variables.
    """
    def __init__(self, config_path: Optional[str] = None):
        self.role_mapping: Dict[str, List[str]] = {}
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.role_mapping = json.load(f)
                logger.info(f"Loaded role mapping from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load role mapping from {config_path}: {e}")

    def get_roles(self, user_email: Optional[str]) -> List[str]:
        """
        Maps a user email to a list of roles.
        """
        if not user_email or user_email == "anonymous":
            return ["public"]

        # 1. Check for exact match in mapping config
        if user_email in self.role_mapping:
            roles = self.role_mapping[user_email]
            if "public" not in roles:
                roles.append("public")
            return roles

        # 2. Fallback to domain-based or hardcoded rules
        roles = ["public"]
        
        # Domain-based rules
        if user_email.endswith("@finance.com"):
            roles.append("finance")
        elif user_email.endswith("@legal.com"):
            roles.append("legal")
        elif user_email == "admin@bank.com":
            roles.append("finance")
            roles.append("admin")
            
        return list(set(roles))

# Singleton instance
ROLE_CONFIG_PATH = os.getenv("ROLE_MAPPING_CONFIG_PATH")
role_manager = RoleManager(ROLE_CONFIG_PATH)

def get_user_roles(user_email: Optional[str]) -> List[str]:
    """Helper function to get roles for a user."""
    return role_manager.get_roles(user_email)
