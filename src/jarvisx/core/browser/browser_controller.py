"""Browser Controller — maps high-level intents to Playwright browser actions."""
import logging
from typing import Optional
from jarvisx.core.browser.playwright_driver import PlaywrightDriver

logger = logging.getLogger(__name__)

class BrowserController:
    """Executes high-level browser commands."""

    _instance: Optional["BrowserController"] = None

    def __init__(self):
        self.driver = PlaywrightDriver()

    @classmethod
    def get_instance(cls) -> "BrowserController":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def search_youtube(self, query: str) -> bool:
        """Search YouTube for the given query."""
        try:
            page = self.driver.get_page()
            page.goto("https://www.youtube.com")
            # Fill the search box
            page.fill("input#search", query)
            page.press("input#search", "Enter")
            # Wait for results
            page.wait_for_selector("ytd-video-renderer", timeout=5000)
            return True
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return False

    def search_google(self, query: str) -> bool:
        """Search Google for the given query."""
        try:
            page = self.driver.get_page()
            page.goto("https://www.google.com")
            # Fill the search box
            page.fill("textarea[name='q']", query)
            page.press("textarea[name='q']", "Enter")
            # Wait for results
            page.wait_for_selector("div#search", timeout=5000)
            return True
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return False

    def open_github(self) -> bool:
        """Open the GitHub homepage."""
        try:
            page = self.driver.get_page()
            page.goto("https://github.com")
            return True
        except Exception as e:
            logger.error(f"Failed to open GitHub: {e}")
            return False

    def search_github(self, query: str) -> bool:
        """Search GitHub for the given query."""
        try:
            page = self.driver.get_page()
            page.goto(f"https://github.com/search?q={query}")
            page.wait_for_selector(".repo-list", timeout=5000)
            return True
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            return False

    def open_chatgpt(self) -> bool:
        """Open the ChatGPT homepage."""
        try:
            page = self.driver.get_page()
            page.goto("https://chat.openai.com")
            return True
        except Exception as e:
            logger.error(f"Failed to open ChatGPT: {e}")
            return False
