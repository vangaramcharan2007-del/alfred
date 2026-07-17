from .browser_permissions import BrowserPermissionManager, BrowserTrustLevel, requires_browser_permission
from .browser_manager import BrowserManager
from .page_controller import PageController
from .element_locator import ElementLocator
from .form_handler import FormHandler
from .extractor import Extractor
from .session_manager import SessionManager
from .observer import Observer
from .screenshot_manager import ScreenshotManager

__all__ = [
    "BrowserPermissionManager",
    "BrowserTrustLevel",
    "requires_browser_permission",
    "BrowserManager",
    "PageController",
    "ElementLocator",
    "FormHandler",
    "Extractor",
    "SessionManager",
    "Observer",
    "ScreenshotManager"
]
