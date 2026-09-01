"""
Unit tests for the Sovereign Linux Bridge Agent & Tools.
"""

import pytest
from jarvisx.agents.linux_agent import LinuxBridgeAgent, LinuxTelemetry
from jarvisx.tools.tool_kernel import ToolRegistry
from jarvisx.tools.builtin_tools import (
    ExecuteLinuxBashTool,
    GetLinuxSystemInfoTool,
    register_builtin_tools,
)


def test_linux_agent_singleton():
    a1 = LinuxBridgeAgent.get_instance()
    a2 = LinuxBridgeAgent.get_instance()
    assert a1 is a2


def test_linux_runtime_detection():
    agent = LinuxBridgeAgent.get_instance()
    runtime = agent.detect_runtime()
    assert runtime in ("wsl", "virtualbox", "native", "bridge")


def test_linux_bash_execution_echo():
    agent = LinuxBridgeAgent.get_instance()
    res = agent.execute_bash("echo 'Hello from Jarvis Linux Agent'")
    assert res["status"] == "success"
    assert res["returncode"] == 0
    assert "Hello from Jarvis Linux Agent" in res["stdout"]


def test_linux_bash_math_computation():
    agent = LinuxBridgeAgent.get_instance()
    res = agent.execute_bash("expr 1500 + 526")
    assert res["status"] == "success"
    assert "2026" in res["stdout"]


def test_linux_system_telemetry():
    agent = LinuxBridgeAgent.get_instance()
    telemetry = agent.get_system_info()
    assert isinstance(telemetry, LinuxTelemetry)
    assert telemetry.is_operational is True
    assert telemetry.memory_total_mb > 0
    assert telemetry.disk_total_gb > 0


def test_linux_bridge_file(tmp_path):
    agent = LinuxBridgeAgent.get_instance()
    src_file = tmp_path / "test_source.txt"
    src_file.write_text("JARVIS_LINUX_BRIDGE_PAYLOAD_2026")

    dst_file = tmp_path / "linux_subfolder" / "test_dest.txt"
    res = agent.bridge_file(str(src_file), str(dst_file))
    assert res["status"] == "success"
    assert dst_file.exists()
    assert dst_file.read_text() == "JARVIS_LINUX_BRIDGE_PAYLOAD_2026"


def test_builtin_linux_tools_registration():
    registry = ToolRegistry.get_instance()
    register_builtin_tools(registry)

    # 1. ExecuteLinuxBashTool
    bash_tool = registry.get("execute_linux_bash")
    assert bash_tool is not None
    res = bash_tool.execute({"command": "echo 'Tool Registry OK'"})
    assert res.status == "success"
    assert "Tool Registry OK" in res.result.get("stdout", "")

    # 2. GetLinuxSystemInfoTool
    info_tool = registry.get("get_linux_system_info")
    assert info_tool is not None
    res_info = info_tool.execute({})
    assert res_info.status == "success"
    assert res_info.result.get("is_operational") is True
