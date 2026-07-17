import logging
from typing import Dict, Any, List
from .browser_manager import BrowserManager

logger = logging.getLogger(__name__)

class Extractor:
    @staticmethod
    async def extract_title(context_id: str = "default", page_id: str = "main") -> str:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        return await page.title()

    @staticmethod
    async def extract_text(context_id: str = "default", page_id: str = "main") -> str:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        return await page.evaluate("document.body.innerText")

    @staticmethod
    async def extract_links(context_id: str = "default", page_id: str = "main") -> List[Dict[str, str]]:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        links = await page.evaluate("""
            Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText,
                href: a.href
            }))
        """)
        return links

    @staticmethod
    async def extract_images(context_id: str = "default", page_id: str = "main") -> List[Dict[str, str]]:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        images = await page.evaluate("""
            Array.from(document.querySelectorAll('img')).map(img => ({
                src: img.src,
                alt: img.alt
            }))
        """)
        return images

    @staticmethod
    async def extract_tables(context_id: str = "default", page_id: str = "main") -> List[Any]:
        # Highly simplified table extraction
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        tables = await page.evaluate("""
            Array.from(document.querySelectorAll('table')).map(table => {
                return Array.from(table.rows).map(row => {
                    return Array.from(row.cells).map(cell => cell.innerText);
                });
            })
        """)
        return tables

    @staticmethod
    async def extract_metadata(context_id: str = "default", page_id: str = "main") -> Dict[str, str]:
        page = await BrowserManager.get_instance().get_page(context_id, page_id)
        meta = await page.evaluate("""
            Array.from(document.querySelectorAll('meta')).reduce((acc, meta) => {
                const name = meta.getAttribute('name') || meta.getAttribute('property');
                if (name) acc[name] = meta.getAttribute('content');
                return acc;
            }, {})
        """)
        return meta
