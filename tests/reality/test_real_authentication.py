import pytest
from pathlib import Path
import sys

def test_real_authentication_logic():
    # Test auth functions directly
    from jarvisx.automation.real_project_builder import RealProjectBuilder
    builder = RealProjectBuilder(base_dir="var/test_real_auth")
    res = builder.build_fullstack_auth_app(app_name="auth_app")
    
    backend_dir = res["backend_dir"]
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
        
    from auth import hash_password, verify_password, create_token
    
    password = "secretPassword123!"
    h = hash_password(password)
    assert verify_password(password, h) is True
    assert verify_password("wrong", h) is False
    
    token = create_token("ramcharan")
    assert token is not None
    assert "." in token
