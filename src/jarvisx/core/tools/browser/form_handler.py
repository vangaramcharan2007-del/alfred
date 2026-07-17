import logging
from .browser_permissions import requires_browser_permission, BrowserTrustLevel
from .element_locator import ElementLocator

logger = logging.getLogger(__name__)

class FormHandler:
    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.INTERACT)
    async def click(strategy: str, selector: str, context_id: str = "default", page_id: str = "main"):
        locator = await ElementLocator.get_locator(strategy, selector, context_id, page_id)
        logger.info(f"Clicking element: {strategy}={selector}")
        await locator.first.click()

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.INTERACT)
    async def type(strategy: str, selector: str, text: str, context_id: str = "default", page_id: str = "main"):
        locator = await ElementLocator.get_locator(strategy, selector, context_id, page_id)
        logger.info(f"Typing into element: {strategy}={selector}")
        await locator.first.fill(text)

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.INTERACT)
    async def select(strategy: str, selector: str, value: str, context_id: str = "default", page_id: str = "main"):
        locator = await ElementLocator.get_locator(strategy, selector, context_id, page_id)
        logger.info(f"Selecting {value} in element: {strategy}={selector}")
        await locator.first.select_option(value)

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.INTERACT)
    async def scroll(direction: str = "down", context_id: str = "default", page_id: str = "main"):
        from .browser_manager import BrowserManager
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        if direction == "down":
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
        elif direction == "up":
            await page.evaluate("window.scrollBy(0, -window.innerHeight)")
        elif direction == "top":
            await page.evaluate("window.scrollTo(0, 0)")
        elif direction == "bottom":
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.INTERACT)
    async def hover(strategy: str, selector: str, context_id: str = "default", page_id: str = "main"):
        locator = await ElementLocator.get_locator(strategy, selector, context_id, page_id)
        await locator.first.hover()

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.INTERACT)
    async def press_key(key: str, context_id: str = "default", page_id: str = "main"):
        from .browser_manager import BrowserManager
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        await page.keyboard.press(key)

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.INTERACT)
    async def upload_file(strategy: str, selector: str, file_path: str, context_id: str = "default", page_id: str = "main"):
        locator = await ElementLocator.get_locator(strategy, selector, context_id, page_id)
        await locator.first.set_input_files(file_path)
