from enum import IntEnum

class DesktopTrustLevel(IntEnum):
    READ_ONLY = 1        # Inspect screen, clipboard read, list windows
    INPUT_CONTROL = 2    # Mouse/Keyboard, write clipboard
    PROCESS_CONTROL = 3  # Start/Stop processes, resize/close windows
    SYSTEM_CONTROL = 4   # OS-level settings, shutdown

class DesktopPermissionManager:
    _current_level: DesktopTrustLevel = DesktopTrustLevel.READ_ONLY

    @classmethod
    def set_level(cls, level: DesktopTrustLevel):
        cls._current_level = level

    @classmethod
    def require(cls, required_level: DesktopTrustLevel):
        if cls._current_level < required_level:
            raise PermissionError(f"Operation requires DesktopTrustLevel {required_level.name}, but current level is {cls._current_level.name}")
