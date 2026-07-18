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
    "file explorer": "explorer",
    "edge": "msedge",
    "firefox": "firefox",
    "notepad++": "notepad++"
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
            # os.startfile is the most robust way to launch GUI apps on Windows
            # without tying them to the console or suppressing their windows.
            if hasattr(os, 'startfile'):
                os.startfile(cmd)
                return True
            else:
                subprocess.Popen(
                    cmd, 
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
                return True
        except Exception as e:
            logger.error(f"Failed to launch {target}: {e}")
            return False
