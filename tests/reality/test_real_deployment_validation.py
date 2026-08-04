import pytest
from jarvisx.automation.real_project_builder import RealProjectBuilder
from jarvisx.deployment.deployer import DeploymentEngine

def test_real_deployment_validation():
    builder = RealProjectBuilder(base_dir="var/test_real_deploy")
    app_info = builder.build_fullstack_auth_app(app_name="deploy_app")
    
    framework = DeploymentEngine.detect_framework(app_info["app_dir"])
    assert "Python" in framework or "HTTP" in framework
    
    deploy_res = DeploymentEngine.deploy_app(app_info["app_dir"], app_name="deploy_app")
    assert deploy_res.config_generated is True
    assert deploy_res.env_valid is True
    assert deploy_res.deployed is True
    assert "8080" in deploy_res.deployment_url
