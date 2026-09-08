"""
Deterministic CDP / Playwright Browser Automation Driver for Jarvis X.
Uses direct protocol connections, strict semantic locators, and network/DOM idle verification.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from jarvisx.harness.aov_engine import (
    AOVResult,
    ClosedLoopHarness,
    StateObserver,
    rule_any_state_delta,
)

logger = logging.getLogger("jarvisx.browser_driver")


@dataclass
class BrowserElementState:
    selector: str
    is_visible: bool
    is_enabled: bool
    text: str
    bounding_box: Optional[Dict[str, float]]


class DeterministicBrowserDriver:
    """High-reliability headless/headed browser driver with verified execution."""

    _instance: Optional[DeterministicBrowserDriver] = None

    @classmethod
    def get_instance(cls) -> DeterministicBrowserDriver:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.active_page = None
        self.harness = ClosedLoopHarness(max_retries=2, retry_delay_sec=0.3)

    async def initialize(self, headless: bool = True, cdp_url: Optional[str] = None):
        """Initializes playwright browser session or connects to existing CDP."""
        if self.active_page is not None:
            return

        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()

        if cdp_url:
            logger.info(f"[BrowserDriver] Connecting to existing CDP at {cdp_url}...")
            self.browser = await self.playwright.chromium.connect_over_cdp(cdp_url)
            self.context = self.browser.contexts[0] if self.browser.contexts else await self.browser.new_context()
            self.active_page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        else:
            logger.info(f"[BrowserDriver] Launching Chromium (headless={headless})...")
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            self.context = await self.browser.new_context(viewport={"width": 1920, "height": 1080})
            self.active_page = await self.context.new_page()

    async def navigate(self, url: str, wait_until: str = "domcontentloaded", timeout_ms: int = 15000) -> Dict[str, Any]:
        """Navigates to URL and awaits deterministic page state."""
        if not self.active_page:
            await self.initialize(headless=True)

        t0 = time.perf_counter()
        resp = await self.active_page.goto(url, wait_until=wait_until, timeout=timeout_ms)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        title = await self.active_page.title()
        status_code = resp.status if resp else 200

        return {
            "url": self.active_page.url,
            "title": title,
            "status": status_code,
            "elapsed_ms": round(elapsed_ms, 2),
        }

    async def click_element(self, selector: str, timeout_ms: int = 5000) -> Dict[str, Any]:
        """Finds element using semantic or CSS selector, awaits clickability, and clicks."""
        if not self.active_page:
            raise RuntimeError("Browser not initialized.")

        locator = self.active_page.locator(selector).first
        await locator.wait_for(state="visible", timeout=timeout_ms)
        await locator.click(timeout=timeout_ms)

        return {
            "clicked": selector,
            "new_url": self.active_page.url,
        }

    async def type_into_element(self, selector: str, text: str, timeout_ms: int = 5000) -> Dict[str, Any]:
        """Fills input element and verifies entered value matches."""
        if not self.active_page:
            raise RuntimeError("Browser not initialized.")

        locator = self.active_page.locator(selector).first
        await locator.wait_for(state="visible", timeout=timeout_ms)
        await locator.fill(text, timeout=timeout_ms)
        val = await locator.input_value()

        if val != text:
            raise ValueError(f"Value mismatch after fill: expected '{text}', got '{val}'")

        return {
            "selector": selector,
            "value": val,
            "verified": True,
        }

    async def evaluate_js(self, expression: str) -> Any:
        """Evaluates JS in the page context."""
        if not self.active_page:
            raise RuntimeError("Browser not initialized.")
        return await self.active_page.evaluate(expression)

    async def get_page_summary(self) -> Dict[str, Any]:
        """Returns structured DOM state without dumping 50,000 raw HTML tokens."""
        if not self.active_page:
            return {}

        title = await self.active_page.title()
        url = self.active_page.url
        # Extract meaningful interactive elements
        elements_summary = await self.active_page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], [role="button"]'))
                .slice(0, 10).map(b => b.innerText || b.value || b.getAttribute('aria-label') || 'unnamed');
            const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), textarea'))
                .slice(0, 10).map(i => i.placeholder || i.name || i.id || 'unnamed');
            return { buttons, inputs };
        }""")

        return {
            "title": title,
            "url": url,
            "interactive_elements": elements_summary,
        }

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.active_page = None
        self.context = None
        self.browser = None
        self.playwright = None
