from enum import Enum, auto

class VisionTrustLevel(Enum):
    NONE = auto()
    SCREENSHOT_ONLY = auto()
    OCR_READ = auto()
    FULL_VISION = auto()

class VisionPermissionManager:
    _current_level = VisionTrustLevel.NONE

    @classmethod
    def set_level(cls, level: VisionTrustLevel):
        cls._current_level = level

    @classmethod
    def require(cls, required_level: VisionTrustLevel):
        if cls._current_level.value < required_level.value:
            raise PermissionError(
                f"Vision permission denied. Required: {required_level.name}, Current: {cls._current_level.name}"
            )
