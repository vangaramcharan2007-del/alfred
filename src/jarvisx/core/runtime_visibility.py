"""Runtime Visibility — controls how agent processes are displayed to the user."""
from enum import Enum
from typing import Optional


class VisibilityMode(str, Enum):
    DEBUG = "DEBUG"           # Separate terminal per agent, verbose logs
    BACKGROUND = "BACKGROUND" # Hidden processes, file-based logs
    HEADLESS = "HEADLESS"     # Single Alfred process visible, everything else silent


class RuntimeVisibility:
    """Singleton that holds the current visibility mode for the runtime."""

    _instance: Optional["RuntimeVisibility"] = None
    _mode: VisibilityMode = VisibilityMode.HEADLESS   # production default

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls) -> "RuntimeVisibility":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None
        cls._mode = VisibilityMode.HEADLESS

    # --- Mode accessors ---

    @classmethod
    def set_mode(cls, mode: VisibilityMode):
        cls._mode = mode

    @classmethod
    def get_mode(cls) -> VisibilityMode:
        return cls._mode

    @classmethod
    def is_debug(cls) -> bool:
        return cls._mode == VisibilityMode.DEBUG

    @classmethod
    def is_headless(cls) -> bool:
        return cls._mode == VisibilityMode.HEADLESS

    @classmethod
    def is_background(cls) -> bool:
        return cls._mode == VisibilityMode.BACKGROUND

    @classmethod
    def should_show_agent_terminals(cls) -> bool:
        """Only DEBUG mode opens visible terminals for agents."""
        return cls._mode == VisibilityMode.DEBUG

    @classmethod
    def should_log_to_files(cls) -> bool:
        """BACKGROUND and HEADLESS redirect logs to files."""
        return cls._mode in (VisibilityMode.BACKGROUND, VisibilityMode.HEADLESS)
