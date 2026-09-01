"""
Unit tests for Linux Native Desktop & Kiosk Deployer.
"""

from pathlib import Path
import pytest
from jarvisx.gui.linux_native_desktop_deployer import LinuxNativeDesktopDeployer
from jarvisx.tools.tool_kernel import ToolRegistry
from jarvisx.tools.builtin_tools import register_builtin_tools, DeployLinuxNativeHUDTool


def test_desktop_entry_generation_syntax():
    deployer = LinuxNativeDesktopDeployer.get_instance()
    entry = deployer.generate_desktop_entry_content("/usr/local/bin/test_launcher.sh")
    assert "[Desktop Entry]" in entry
    assert "Name=Spider-Man E.V. Workstation" in entry
    assert "Exec=/bin/bash \"/usr/local/bin/test_launcher.sh\"" in entry
    assert "X-Cinnamon-Autostart-enabled=true" in entry


def test_kiosk_launcher_script_syntax():
    deployer = LinuxNativeDesktopDeployer.get_instance()
    script = deployer.generate_kiosk_launcher_script("/path/to/server.py")
    assert "#!/bin/bash" in script
    assert "DISPLAY=:0" in script
    assert "python3 \"/path/to/server.py\"" in script
    assert "firefox" in script


def test_deploy_to_linux_environment(tmp_path):
    deployer = LinuxNativeDesktopDeployer.get_instance()
    res = deployer.deploy_to_linux_environment(output_dir=str(tmp_path))
    assert res["status"] == "success"
    assert Path(res["kiosk_script"]).exists()
    assert Path(res["desktop_entry"]).exists()


def test_builtin_tool_deploy_linux_native_hud():
    registry = ToolRegistry.get_instance()
    register_builtin_tools(registry)

    tool = registry.get("deploy_linux_native_hud")
    assert tool is not None
    res = tool.execute({})
    assert res.status == "success"
    assert "deployed_path" in res.result
