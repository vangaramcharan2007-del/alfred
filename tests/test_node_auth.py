import pytest
from jarvisx.security.node_auth import NodeAuthenticator

def test_node_authentication_success():
    auth = NodeAuthenticator()
    auth.register_trusted_node("gaming_laptop", secret_key="super_secret_123")
    
    assert auth.authenticate_node("gaming_laptop", provided_key="super_secret_123") == True

def test_node_authentication_failure():
    auth = NodeAuthenticator()
    auth.register_trusted_node("gaming_laptop", secret_key="super_secret_123")
    
    # Wrong key
    assert auth.authenticate_node("gaming_laptop", provided_key="wrong_key") == False
    
    # Unknown node
    assert auth.authenticate_node("unknown_laptop", provided_key="super_secret_123") == False

def test_unauthorized_node_rejection():
    auth = NodeAuthenticator()
    auth.register_trusted_node("work_laptop", secret_key="key", permission_level="standard", allowed_capabilities=["code_review"])
    
    # Valid auth
    assert auth.authenticate_node("work_laptop", "key") == True
    
    # Allowed capability
    assert auth.authorize_task("work_laptop", ["code_review"]) == True
    
    # Denied capability (should be rejected since it's restricted)
    assert auth.authorize_task("work_laptop", ["video_editing"]) == False

def test_node_revocation():
    auth = NodeAuthenticator()
    auth.register_trusted_node("gaming_laptop", secret_key="super_secret_123")
    
    assert auth.authenticate_node("gaming_laptop", provided_key="super_secret_123") == True
    
    auth.revoke_node("gaming_laptop")
    
    # Should now fail even with correct key
    assert auth.authenticate_node("gaming_laptop", provided_key="super_secret_123") == False
