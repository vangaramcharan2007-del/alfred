"""
Unit tests for the Spider-Man EV Minimalist Workstation & Voice-Activated Linux HUD.
"""

import json
import urllib.request
import pytest
from jarvisx.gui.spiderman_linux_hud import SpiderManLinuxHUDServer, HTML_TEMPLATE, EV_SYSTEM_PROMPTS
from jarvisx.tools.tool_kernel import ToolRegistry
from jarvisx.tools.builtin_tools import register_builtin_tools, LaunchSpiderManEVHUDTool


def test_html_template_contains_ev_and_spidey_elements():
    assert "SPIDER-MAN" in HTML_TEMPLATE
    assert "EV" in HTML_TEMPLATE
    assert "ADHD-FRIENDLY" in HTML_TEMPLATE
    assert "00f0ff" in HTML_TEMPLATE  # Electric Venom Cyan
    assert "ff003c" in HTML_TEMPLATE  # Stark Crimson Red
    assert "speechSynthesis" in HTML_TEMPLATE


def test_ev_system_prompts():
    assert "greeting" in EV_SYSTEM_PROMPTS
    assert "cyber_scan" in EV_SYSTEM_PROMPTS
    assert "ai_train" in EV_SYSTEM_PROMPTS
    assert "turbo_cool" in EV_SYSTEM_PROMPTS


def test_spiderman_hud_server_and_endpoints():
    port = 5055
    url = SpiderManLinuxHUDServer.start(port=port, open_browser=False)
    assert url == f"http://localhost:{port}"

    # 1. Test GET / (HTML)
    with urllib.request.urlopen(f"{url}/") as response:
        assert response.status == 200
        html = response.read().decode("utf-8")
        assert "SPIDER-MAN" in html

    # 2. Test GET /api/telemetry
    with urllib.request.urlopen(f"{url}/api/telemetry") as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert "kernel_version" in data
        assert "memory_total_mb" in data

    # 3. Test POST /api/bash
    req = urllib.request.Request(
        f"{url}/api/bash",
        data=json.dumps({"command": "echo 'EV Spidey Bash Test'"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert data["status"] == "success"
        assert "EV Spidey Bash Test" in data["stdout"]

    # 4. Test POST /api/action (cyber_scan)
    req_action = urllib.request.Request(
        f"{url}/api/action",
        data=json.dumps({"action": "cyber_scan"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_action) as response:
        assert response.status == 200
        data = json.loads(response.read().decode("utf-8"))
        assert data["status"] == "success"
        assert len(data["ev_speech"]) > 0


def test_builtin_tool_launch_spiderman_ev_hud():
    registry = ToolRegistry.get_instance()
    register_builtin_tools(registry)

    tool = registry.get("launch_spiderman_ev_hud")
    assert tool is not None
    res = tool.execute({"port": 5056})
    assert res.status == "success"
    assert "http://localhost:5056" in res.result.get("url", "")
