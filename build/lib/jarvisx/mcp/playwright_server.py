"""Playwright Browser Engine Standalone MCP Server for Jarvis X.

Implements programmatic DOM inspection, CSS-selector clicks, text extraction,
and headless Chromium session persistence over standard MCP JSON-RPC 2.0 stdio.

Run directly as an MCP server:
    python -m jarvisx.mcp.playwright_server
"""

from __future__ import annotations
import sys
import json
import asyncio
try:
    from playwright.async_api import async_playwright, Browser, Page, Playwright
except Exception:
    async_playwright, Browser, Page, Playwright = None, None, None, None


# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==========================================
# TOOL SPECIFICATIONS (MCP Protocol)
# ==========================================
PLAYWRIGHT_TOOLS_SPEC = [
    {
        "name": "browser_navigate",
        "description": "Navigates the browser to a specific URL and returns page title.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The target URL to navigate to."}
            },
            "required": ["url"]
        }
    },
    {
        "name": "browser_extract_text",
        "description": "Extracts raw, readable text from a CSS selector (defaults to 'body').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector to extract text from.", "default": "body"}
            }
        }
    },
    {
        "name": "browser_click",
        "description": "Clicks an element in the DOM using a CSS or XPath selector.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS or XPath selector of element to click."}
            },
            "required": ["selector"]
        }
    },
    {
        "name": "browser_type",
        "description": "Types text into an input field defined by a selector.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector for the input element."},
                "text": {"type": "string", "description": "Text to fill into the input field."}
            },
            "required": ["selector", "text"]
        }
    },
    {
        "name": "browser_evaluate_js",
        "description": "Executes arbitrary JavaScript in the context of the current page.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "script": {"type": "string", "description": "JavaScript code string to evaluate."}
            },
            "required": ["script"]
        }
    }
]


# ==========================================
# STATEFUL PLAYWRIGHT SESSION ENGINE
# ==========================================
class PlaywrightSessionEngine:
    """Stateful singleton browser controller for Jarvis X MCP."""

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._lock = asyncio.Lock()

    async def ensure_browser(self, headless: bool = True) -> Page:
        """Lazy-initializes and retains the Chromium browser session."""
        async with self._lock:
            if self._page is None or self._page.is_closed():
                if self._playwright is None:
                    self._playwright = await async_playwright().start()
                if self._browser is None or not self._browser.is_connected():
                    self._browser = await self._playwright.chromium.launch(
                        headless=headless,
                        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                    )
                context = await self._browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                self._page = await context.new_page()
            return self._page

    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL and return title and status."""
        page = await self.ensure_browser()
        try:
            target_url = url if url.startswith(("http://", "https://")) else f"https://{url}"
            resp = await page.goto(target_url, timeout=20000, wait_until="domcontentloaded")
            title = await page.title()
            status = resp.status if resp else 200
            return {
                "status": "success",
                "url": page.url,
                "title": title,
                "http_status": status,
                "message": f"Successfully navigated to {page.url}. Page title: '{title}'"
            }
        except Exception as e:
            return {"status": "failed", "error": f"Navigation failed: {str(e)}"}

    async def extract_text(self, selector: str = "body") -> Dict[str, Any]:
        """Extract clean text from selector with truncation safety."""
        page = await self.ensure_browser()
        try:
            await page.wait_for_selector(selector, timeout=8000)
            text = await page.locator(selector).inner_text()
            truncated = False
            if len(text) > 8000:
                text = text[:8000] + "\n...[TRUNCATED FOR CONTEXT SAFETY]"
                truncated = True
            return {
                "status": "success",
                "selector": selector,
                "text": text,
                "length": len(text),
                "truncated": truncated
            }
        except Exception as e:
            return {"status": "failed", "error": f"Extraction failed for selector '{selector}': {str(e)}"}

    async def click(self, selector: str) -> Dict[str, Any]:
        """Click an element using CSS selector."""
        page = await self.ensure_browser()
        try:
            await page.wait_for_selector(selector, timeout=8000)
            await page.click(selector, timeout=8000)
            try:
                await page.wait_for_load_state("networkidle", timeout=4000)
            except Exception:
                pass
            return {
                "status": "success",
                "action": "click",
                "selector": selector,
                "current_url": page.url,
                "message": f"Successfully clicked '{selector}'."
            }
        except Exception as e:
            return {"status": "failed", "error": f"Click failed on '{selector}': {str(e)}"}

    async def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        """Fill an input element with text."""
        page = await self.ensure_browser()
        try:
            await page.wait_for_selector(selector, timeout=8000)
            await page.fill(selector, text, timeout=8000)
            return {
                "status": "success",
                "action": "type",
                "selector": selector,
                "message": f"Successfully typed into '{selector}'."
            }
        except Exception as e:
            return {"status": "failed", "error": f"Typing failed on '{selector}': {str(e)}"}

    async def evaluate_js(self, script: str) -> Dict[str, Any]:
        """Execute arbitrary JS code in the browser context."""
        page = await self.ensure_browser()
        try:
            res = await page.evaluate(script)
            return {
                "status": "success",
                "result": res,
                "message": f"Script executed successfully."
            }
        except Exception as e:
            return {"status": "failed", "error": f"Script execution failed: {str(e)}"}

    async def close(self):
        """Cleanup browser resources."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._page = None
        self._browser = None
        self._playwright = None


# Singleton instance
_SESSION_ENGINE = PlaywrightSessionEngine()


def get_playwright_engine() -> PlaywrightSessionEngine:
    return _SESSION_ENGINE


# ==========================================
# MCP PROTOCOL STDIO SERVER LOOP
# ==========================================
async def run_mcp_stdio_server():
    """Stdio JSON-RPC 2.0 MCP event loop."""
    engine = get_playwright_engine()
    loop = asyncio.get_event_loop()

    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "jarvisx-playwright-mcp", "version": "1.0.0"}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": PLAYWRIGHT_TOOLS_SPEC}
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "browser_navigate":
                    out = await engine.navigate(args.get("url", ""))
                elif tool_name == "browser_extract_text":
                    out = await engine.extract_text(args.get("selector", "body"))
                elif tool_name == "browser_click":
                    out = await engine.click(args.get("selector", ""))
                elif tool_name == "browser_type":
                    out = await engine.type_text(args.get("selector", ""), args.get("text", ""))
                elif tool_name == "browser_evaluate_js":
                    out = await engine.evaluate_js(args.get("script", ""))
                else:
                    out = {"status": "failed", "error": f"Unknown tool '{tool_name}'"}

                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(out)}]}
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {e}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


def main():
    asyncio.run(run_mcp_stdio_server())


if __name__ == "__main__":
    main()
