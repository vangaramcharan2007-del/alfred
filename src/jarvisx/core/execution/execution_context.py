"""Execution Context — resolves environment placeholders dynamically."""
import os
import platform
import logging
from typing import Dict, Callable, Optional

logger = logging.getLogger(__name__)

class ExecutionContext:
    """Resolves environment placeholders like ${DESKTOP} into absolute paths."""
    
    def __init__(self):
        self._resolvers: Dict[str, Callable[[], str]] = {}
        self.objective_id: Optional[str] = None
        self.current_step: int = 0
        self._register_default_resolvers()

    def _register_default_resolvers(self):
        """Register default cross-platform environment variables."""
        self.register_placeholder("HOME", lambda: os.path.expanduser("~"))
        
        # Desktop
        self.register_placeholder("DESKTOP", lambda: os.path.join(os.path.expanduser("~"), "Desktop"))
        
        # Downloads
        self.register_placeholder("DOWNLOADS", lambda: os.path.join(os.path.expanduser("~"), "Downloads"))
        
        # Temp
        import tempfile
        self.register_placeholder("TEMP", lambda: tempfile.gettempdir())
        
        # Project / Workspace (assume current working directory for now)
        self.register_placeholder("PROJECT", lambda: os.getcwd())
        self.register_placeholder("WORKSPACE", lambda: os.getcwd())
        
        # Android / Termux specific
        self.register_placeholder("TERMUX_HOME", lambda: os.environ.get("HOME", "/data/data/com.termux/files/home"))
        self.register_placeholder("ANDROID_STORAGE", lambda: "/storage/emulated/0")

    def register_placeholder(self, name: str, resolver: Callable[[], str]) -> None:
        """Register a new placeholder and its resolution function."""
        # Normalize name to remove ${} if passed
        clean_name = name.strip("${}")
        self._resolvers[clean_name] = resolver

    def resolve_path(self, template: str) -> str:
        """
        Replace all placeholders in the template with resolved paths.
        E.g., "${DESKTOP}/hello.txt" -> "C:/Users/User/Desktop/hello.txt"
        """
        resolved = template
        for name, resolver in self._resolvers.items():
            placeholder = f"${{{name}}}"
            if placeholder in resolved:
                try:
                    resolved_value = resolver()
                    resolved = resolved.replace(placeholder, resolved_value)
                except Exception as e:
                    logger.error(f"Failed to resolve placeholder {placeholder}: {e}")
        return resolved
