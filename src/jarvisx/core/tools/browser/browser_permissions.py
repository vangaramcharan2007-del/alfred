from enum import IntEnum
import logging

logger = logging.getLogger(__name__)

class BrowserTrustLevel(IntEnum):
    READ_ONLY = 0
    INTERACT = 1
    AUTHENTICATED_ACTIONS = 2
    PURCHASE_ACTIONS = 3
    ADMIN_ACTIONS = 4

class BrowserPermissionManager:
    _current_level = BrowserTrustLevel.INTERACT  # Default for testing

    @classmethod
    def set_level(cls, level: BrowserTrustLevel):
        cls._current_level = level
        logger.info(f"Browser trust level set to {level.name}")

    @classmethod
    def check_permission(cls, required_level: BrowserTrustLevel):
        if cls._current_level < required_level:
            raise PermissionError(
                f"Browser action requires {required_level.name}, current level is {cls._current_level.name}"
            )

def requires_browser_permission(level: BrowserTrustLevel):
    def decorator(func):
        # We need to handle async functions
        import asyncio
        from functools import wraps
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                BrowserPermissionManager.check_permission(level)
                return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                BrowserPermissionManager.check_permission(level)
                return func(*args, **kwargs)
            return sync_wrapper
    return decorator
