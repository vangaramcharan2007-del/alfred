import logging
from pathlib import Path
from .browser_manager import BrowserManager

logger = logging.getLogger(__name__)

class SessionManager:
    @staticmethod
    async def save_state(context_id: str = "default", path: str = "var/storageState.json"):
        manager = BrowserManager.get_instance()
        if context_id in manager.contexts:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            await manager.contexts[context_id].storage_state(path=path)
            logger.info(f"Saved session state to {path}")
            return True
        return False

    @staticmethod
    async def restore_state(context_id: str = "default", path: str = "var/storageState.json"):
        if Path(path).exists():
            manager = BrowserManager.get_instance()
            # If context already exists, we cannot apply state post-creation easily without a new context
            # We'll rely on the BrowserManager.create_context being called with storage_state instead
            await manager.close_context(context_id)
            await manager.create_context(context_id, storage_state=path)
            logger.info(f"Restored session state from {path}")
            return True
        return False
