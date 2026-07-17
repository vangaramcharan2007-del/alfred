"""Application Launcher — OS-level application launching without visible consoles."""
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

# Map common spoken names to executable commands or paths
_APP_MAP = {
    "vscode": "code",
    "visual studio code": "code",
    "chrome": "chrome",
    "browser": "chrome",  # fallback
    "notepad": "notepad",
    "calculator": "calc",
    "file explorer": "explorer"
}

class AppLauncher:
    """Launches local OS applications silently."""

    @classmethod
    def launch(cls, target: str) -> bool:
        """Launch the specified application. Returns True if successful."""
        target_lower = target.lower().strip()
        cmd = _APP_MAP.get(target_lower)
        
        if not cmd:
            logger.error(f"Application not found in map: {target}")
            return False

        try:
            # We want to launch the app as a background process completely detached,
            # with no console window. CREATE_NO_WINDOW suppresses the cmd prompt.
            # Using shell=True for 'code', 'explorer', 'chrome' helps Windows find them via PATH.
            flags = subprocess.CREATE_NO_WINDOW
            
            subprocess.Popen(
                cmd, 
                shell=True, 
                creationflags=flags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            return True
        except Exception as e:
            logger.error(f"Failed to launch {target}: {e}")
            return False
