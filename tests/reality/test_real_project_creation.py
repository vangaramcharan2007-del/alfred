import pytest
from pathlib import Path
from jarvisx.automation.real_project_builder import RealProjectBuilder

def test_real_project_creation():
    builder = RealProjectBuilder(base_dir="var/test_real_project")
    res = builder.build_fullstack_auth_app(app_name="test_app")
    
    assert Path(res["app_dir"]).exists()
    assert Path(res["frontend_dir"] + "/index.html").exists()
    assert Path(res["backend_dir"] + "/server.py").exists()
    assert Path(res["backend_dir"] + "/database.py").exists()
    assert Path(res["backend_dir"] + "/auth.py").exists()
    assert Path(res["backend_dir"] + "/test_app.py").exists()
