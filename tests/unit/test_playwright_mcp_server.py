"""Unit & Integration Verification for Jarvis X Playwright MCP Server (Sprint 4)."""

import pytest
import asyncio
import json
from jarvisx.mcp.playwright_server import (
    PlaywrightSessionEngine,
    PLAYWRIGHT_TOOLS_SPEC,
    get_playwright_engine
)


@pytest.mark.asyncio
async def test_playwright_engine_stateful_session_and_navigation():
    """Test stateful browser session lifecycle, navigation, and DOM text extraction."""
    engine = PlaywrightSessionEngine()
    try:
        # 1. Test Navigation
        nav_res = await engine.navigate("https://example.com")
        assert nav_res["status"] == "success"
        assert "Example Domain" in nav_res["title"]
        assert "example.com" in nav_res["url"]

        # 2. Test Text Extraction (Default body)
        text_res = await engine.extract_text("body")
        assert text_res["status"] == "success"
        assert "Example Domain" in text_res["text"]
        assert not text_res["truncated"]

        # 3. Test JS Evaluation in same active session
        js_res = await engine.evaluate_js("document.querySelectorAll('p').length")
        assert js_res["status"] == "success"
        assert js_res["result"] >= 1

        # 4. Test Selector Extraction (h1 element)
        h1_res = await engine.extract_text("h1")
        assert h1_res["status"] == "success"
        assert "Example Domain" in h1_res["text"]
    finally:
        await engine.close()


def test_playwright_tools_spec_schema():
    """Verify MCP protocol tool schemas and definitions."""
    tool_names = [t["name"] for t in PLAYWRIGHT_TOOLS_SPEC]
    assert "browser_navigate" in tool_names
    assert "browser_extract_text" in tool_names
    assert "browser_click" in tool_names
    assert "browser_type" in tool_names
    assert "browser_evaluate_js" in tool_names
