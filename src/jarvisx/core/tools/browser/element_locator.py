import logging
from typing import Dict, Any
from playwright.async_api import Page, Locator
from .browser_manager import BrowserManager

logger = logging.getLogger(__name__)

class ElementLocator:
    @staticmethod
    async def locate(
        strategy: str, 
        selector: str, 
        context_id: str = "default", 
        page_id: str = "main"
    ) -> Dict[str, Any]:
        """
        Locates an element and returns its metadata.
        Strategies: text, css, role, placeholder, xpath
        """
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        locator: Locator = None

        if strategy == "text":
            locator = page.get_by_text(selector)
        elif strategy == "css":
            locator = page.locator(selector)
        elif strategy == "role":
            locator = page.get_by_role(selector)
        elif strategy == "placeholder":
            locator = page.get_by_placeholder(selector)
        elif strategy == "xpath":
            locator = page.locator(f"xpath={selector}")
        else:
            raise ValueError(f"Unknown locator strategy: {strategy}")

        count = await locator.count()
        confidence = 0.99 if count == 1 else (0.5 if count > 1 else 0.0)

        return {
            "strategy": strategy,
            "selector": selector,
            "confidence": confidence,
            "count": count
        }

    @staticmethod
    async def get_locator(
        strategy: str, 
        selector: str, 
        context_id: str = "default", 
        page_id: str = "main"
    ) -> Locator:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        if strategy == "text":
            return page.get_by_text(selector)
        elif strategy == "css":
            return page.locator(selector)
        elif strategy == "role":
            return page.get_by_role(selector)
        elif strategy == "placeholder":
            return page.get_by_placeholder(selector)
        elif strategy == "xpath":
            return page.locator(f"xpath={selector}")
        else:
            return page.locator(selector)
