import logging
from pathlib import Path
from .browser_manager import BrowserManager
from .element_locator import ElementLocator

logger = logging.getLogger(__name__)

class ScreenshotManager:
    @staticmethod
    async def capture_viewport(path: str = "var/screenshot.png", context_id: str = "default", page_id: str = "main") -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        await page.screenshot(path=path)
        logger.info(f"Captured viewport to {path}")
        return path

    @staticmethod
    async def capture_full_page(path: str = "var/screenshot_full.png", context_id: str = "default", page_id: str = "main") -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        await page.screenshot(path=path, full_page=True)
        logger.info(f"Captured full page to {path}")
        return path

    @staticmethod
    async def capture_element(strategy: str, selector: str, path: str = "var/element.png", context_id: str = "default", page_id: str = "main") -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        locator = await ElementLocator.get_locator(strategy, selector, context_id, page_id)
        await locator.first.screenshot(path=path)
        return path
