"""Playwright Driver — manages the Playwright browser instance."""
import logging
from playwright.sync_api import sync_playwright, Browser, Page

logger = logging.getLogger(__name__)

class PlaywrightDriver:
    """Manages a visible Playwright browser session."""

    def __init__(self):
        self._playwright = None
        self._browser: Browser = None
        self._page: Page = None

    def start(self):
        """Start the Playwright instance if not already running."""
        if not self._playwright:
            self._playwright = sync_playwright().start()
            # Headless=False so the user can visibly see the actions
            self._browser = self._playwright.chromium.launch(headless=False)
            self._page = self._browser.new_page()

    def get_page(self) -> Page:
        """Returns the active page, starting the browser if necessary."""
        if not self._page or self._page.is_closed():
            if self._browser and not self._browser.is_connected():
                self.stop()
            self.start()
            if self._page.is_closed():
                self._page = self._browser.new_page()
        return self._page

    def stop(self):
        """Stop the Playwright instance."""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        self._page = None
