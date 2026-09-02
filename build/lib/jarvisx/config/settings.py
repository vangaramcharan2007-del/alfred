"""Global developer settings and diagnostic toggles."""
import os

class DeveloperSettings:
    """Diagnostic toggles for Developer Mode."""
    
    # Enable verbose diagnostic logging
    VERBOSE_LOGGING = os.environ.get("JARVISX_DEV_VERBOSE", "0") == "1"
    
    # Enable visual UI in agents
    ENABLE_VISUAL_UI = os.environ.get("JARVISX_DEV_UI", "1") == "1"
    
    # Enable strict lock timeouts (fails faster for debugging)
    STRICT_LOCKS = os.environ.get("JARVISX_DEV_STRICT_LOCKS", "0") == "1"
    
    # Trace method execution in ToolRegistry
    TRACE_TOOL_EXECUTION = os.environ.get("JARVISX_DEV_TRACE_TOOLS", "0") == "1"
    
    @classmethod
    def enable_developer_mode(cls):
        """Turn on all diagnostics."""
        cls.VERBOSE_LOGGING = True
        cls.ENABLE_VISUAL_UI = True
        cls.STRICT_LOCKS = True
        cls.TRACE_TOOL_EXECUTION = True
