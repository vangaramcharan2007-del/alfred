import logging
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Singleton manager for Playwright lifecycle.
    """
    _instance = None

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}

    @classmethod
    def get_instance(cls) -> "BrowserManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def launch(self, headless: bool = True) -> Browser:
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        if not self.browser:
            logger.info(f"Launching Chromium browser (headless={headless})")
            self.browser = await self.playwright.chromium.launch(headless=headless)
        return self.browser

    async def create_context(self, context_id: str = "default", storage_state: Optional[str] = None) -> BrowserContext:
        await self.launch()
        if context_id not in self.contexts:
            logger.info(f"Creating browser context: {context_id}")
            self.contexts[context_id] = await self.browser.new_context(storage_state=storage_state)
        return self.contexts[context_id]

    async def create_page(self, context_id: str = "default", page_id: str = "main") -> Page:
        context = await self.create_context(context_id)
        page_key = f"{context_id}:{page_id}"
        if page_key not in self.pages:
            logger.info(f"Creating new page: {page_id} in context {context_id}")
            self.pages[page_key] = await context.new_page()
        return self.pages[page_key]

    async def get_page(self, context_id: str = "default", page_id: str = "main") -> Page:
        page_key = f"{context_id}:{page_id}"
        if page_key not in self.pages:
            return await self.create_page(context_id, page_id)
        return self.pages[page_key]

    async def close_page(self, context_id: str = "default", page_id: str = "main"):
        page_key = f"{context_id}:{page_id}"
        if page_key in self.pages:
            logger.info(f"Closing page {page_key}")
            await self.pages[page_key].close()
            del self.pages[page_key]

    async def close_context(self, context_id: str = "default"):
        if context_id in self.contexts:
            # Close all pages in this context
            pages_to_close = [k for k in self.pages.keys() if k.startswith(f"{context_id}:")]
            for pk in pages_to_close:
                await self.pages[pk].close()
                del self.pages[pk]
            
            logger.info(f"Closing context {context_id}")
            await self.contexts[context_id].close()
            del self.contexts[context_id]

    async def shutdown(self):
        logger.info("Shutting down Browser Manager")
        for context in list(self.contexts.values()):
            await context.close()
        self.contexts.clear()
        self.pages.clear()
        
        if self.browser:
            await self.browser.close()
            self.browser = None
            
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
