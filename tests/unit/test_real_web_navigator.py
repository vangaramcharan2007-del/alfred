"""Unit verification for AutonomousWebResearcher ReAct loop."""

import pytest
import asyncio
from jarvisx.automation.real_web_navigator import AutonomousWebResearcher


@pytest.mark.asyncio
async def test_autonomous_web_researcher_tool_execution():
    """Test local execution of navigation, text extraction, and js evaluation tools."""
    researcher = AutonomousWebResearcher()
    try:
        # 1. Test direct tool navigation
        nav_msg = await researcher.execute_tool_locally("browser_navigate", {"url": "https://example.com"})
        assert "Example Domain" in nav_msg or "navigated" in nav_msg.lower()

        # 2. Test text extraction
        text_out = await researcher.execute_tool_locally("browser_extract_text", {"selector": "h1"})
        assert "Example Domain" in text_out

        # 3. Test js evaluation
        js_out = await researcher.execute_tool_locally("browser_evaluate_js", {"script": "1 + 1"})
        assert "2" in js_out
    finally:
        await researcher.engine.close()


@pytest.mark.asyncio
async def test_autonomous_web_researcher_task_fallback():
    """Test full run_research_task fallback execution when remote cluster endpoint is handled gracefully."""
    researcher = AutonomousWebResearcher(node_ip="http://127.0.0.1:9999")
    try:
        res = await researcher.run_research_task("Navigate to 'https://example.com' and extract body text.")
        assert res["status"] == "success"
        assert len(res["synthesis"]) > 0
    finally:
        await researcher.engine.close()
