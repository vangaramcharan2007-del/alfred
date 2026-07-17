from enum import IntEnum
import logging

logger = logging.getLogger(__name__)

class TrustLevel(IntEnum):
    LEVEL_0_READONLY = 0
    LEVEL_1_FILES = 1
    LEVEL_2_APPS = 2
    LEVEL_3_GIT = 3
    LEVEL_4_SHELL = 4
    LEVEL_5_ADMIN = 5

class PermissionManager:
    _current_level = TrustLevel.LEVEL_4_SHELL  # Default for this milestone

    @classmethod
    def set_level(cls, level: TrustLevel):
        cls._current_level = level
        logger.info(f"Trust level set to {level.name}")

    @classmethod
    def check_permission(cls, required_level: TrustLevel):
        if cls._current_level < required_level:
            raise PermissionError(f"Action requires {required_level.name}, current level is {cls._current_level.name}")

def requires_permission(level: TrustLevel):
    def decorator(func):
        def wrapper(*args, **kwargs):
            PermissionManager.check_permission(level)
            return func(*args, **kwargs)
        return wrapper
    return decorator
