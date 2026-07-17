"""Browser Launcher — OS-level website launching without visible consoles."""
import logging
import webbrowser

logger = logging.getLogger(__name__)

# Map common spoken website names to URLs
_SITE_MAP = {
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "chatgpt": "https://chat.openai.com",
}

class BrowserLauncher:
    """Launches websites in the default system browser."""

    @classmethod
    def launch(cls, target: str) -> bool:
        """Launch the specified website. Returns True if successful."""
        target_lower = target.lower().strip()
        url = _SITE_MAP.get(target_lower)
        
        if not url:
            logger.error(f"Website not found in map: {target}")
            return False

        try:
            # webbrowser.open opens the URL in the default browser.
            # This relies on the OS default browser configuration.
            success = webbrowser.open(url)
            return success
        except Exception as e:
            logger.error(f"Failed to open website {target}: {e}")
            return False
