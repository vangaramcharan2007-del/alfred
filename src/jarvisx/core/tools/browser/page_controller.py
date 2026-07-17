import logging
from playwright.async_api import Page
from .browser_manager import BrowserManager
from .browser_permissions import requires_browser_permission, BrowserTrustLevel

logger = logging.getLogger(__name__)

class PageController:
    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.READ_ONLY)
    async def navigate(url: str, context_id: str = "default", page_id: str = "main", timeout: int = 30000) -> bool:
        manager = BrowserManager.get_instance()
        page = await manager.get_page(context_id, page_id)
        logger.info(f"Navigating to {url}")
        try:
            await page.goto(url, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.READ_ONLY)
    async def reload(context_id: str = "default", page_id: str = "main") -> bool:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        await page.reload()
        return True

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.READ_ONLY)
    async def back(context_id: str = "default", page_id: str = "main") -> bool:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        await page.go_back()
        return True

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.READ_ONLY)
    async def forward(context_id: str = "default", page_id: str = "main") -> bool:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        await page.go_forward()
        return True

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.READ_ONLY)
    async def new_tab(context_id: str = "default", new_page_id: str = "tab2") -> Page:
        return await BrowserManager.get_instance().create_page(context_id, new_page_id)

    @staticmethod
    @requires_browser_permission(BrowserTrustLevel.READ_ONLY)
    async def close_tab(context_id: str = "default", page_id: str = "main"):
        await BrowserManager.get_instance().close_page(context_id, page_id)

    @staticmethod
    async def current_url(context_id: str = "default", page_id: str = "main") -> str:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        return page.url

    @staticmethod
    async def title(context_id: str = "default", page_id: str = "main") -> str:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        return await page.title()
