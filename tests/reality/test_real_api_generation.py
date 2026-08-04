import pytest
from jarvisx.automation.real_project_builder import RealProjectBuilder
from jarvisx.verification.artifact_verifier import ArtifactVerifier

def test_real_api_generation_and_verification():
    builder = RealProjectBuilder(base_dir="var/test_real_api")
    app_info = builder.build_fullstack_auth_app(app_name="api_app")
    
    ver_res = ArtifactVerifier.verify_app_artifact(app_info)
    assert ver_res.files_exist is True
    assert ver_res.tests_pass is True
    assert ver_res.application_starts is True
    assert ver_res.endpoints_respond is True
    assert ver_res.is_valid is True
