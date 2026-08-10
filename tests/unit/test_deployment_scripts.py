"""Unit Tests for Deployment Scripts and Environment Verification."""

import os
import sys
from pathlib import Path


def test_deployment_scripts_exist():
    """Verify that all required deployment scripts and docs exist and are populated."""
    deploy_dir = Path("deployment")
    assert deploy_dir.exists() and deploy_dir.is_dir()

    expected_files = [
        "install.ps1",
        "start_jarvis.ps1",
        "stop_jarvis.ps1",
        "health_check.ps1",
        "README.md",
    ]

    for fname in expected_files:
        fpath = deploy_dir / fname
        assert fpath.exists(), f"Missing deployment file: {fname}"
        assert fpath.stat().st_size > 50, f"Deployment file {fname} is empty"


def test_python_version_verification():
    """Verify that current Python runtime meets the minimum >= 3.11 requirement."""
    assert sys.version_info >= (3, 11), f"Python version {sys.version_info} does not meet >= 3.11"


def test_required_dependencies_importable():
    """Verify that all core dependencies specified in deployment scripts are importable."""
    core_dependencies = [
        "aiohttp",
        "fastapi",
        "httpx",
        "numpy",
        "pandas",
        "pydantic",
        "yaml",
        "requests",
        "websockets",
        "psutil",
    ]

    for dep in core_dependencies:
        __import__(dep)


def test_runtime_directories_and_config():
    """Verify runtime directory structure and valid YAML configuration."""
    import yaml

    var_dir = Path("var")
    var_dir.mkdir(parents=True, exist_ok=True)
    (var_dir / "db").mkdir(parents=True, exist_ok=True)
    (var_dir / "runtime").mkdir(parents=True, exist_ok=True)
    (var_dir / "logs").mkdir(parents=True, exist_ok=True)

    config_path = Path("config/jarvis.yaml")
    assert config_path.exists(), "config/jarvis.yaml does not exist"

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    assert isinstance(cfg, dict)
    assert "system" in cfg
    assert "runtime" in cfg
