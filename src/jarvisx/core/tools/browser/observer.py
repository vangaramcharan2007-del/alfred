import logging
from .browser_manager import BrowserManager

logger = logging.getLogger(__name__)

class Observer:
    @staticmethod
    async def wait_for_page_ready(context_id: str = "default", page_id: str = "main"):
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        await page.wait_for_load_state("networkidle")

    @staticmethod
    async def detect_login_required(context_id: str = "default", page_id: str = "main") -> bool:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        content = await page.content()
        return "log in" in content.lower() or "sign in" in content.lower()

    @staticmethod
    async def detect_navigation_complete(context_id: str = "default", page_id: str = "main"):
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        await page.wait_for_load_state("domcontentloaded")
