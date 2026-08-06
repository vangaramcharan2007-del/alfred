"""Alfred Windows Startup Manager (Layer 2 - Startup).

Detects operating system, manages Windows startup registration/hooks,
validates startup configuration, and executes safe system initialization.
"""

import json
import os
import sys
import time
from typing import Any, Dict, Optional

from jarvisx.observability.crash_logger import StructuredCrashLogger


class StartupManager:
    """Zero-fluff production Windows startup manager and OS launcher."""

    def __init__(self, config_dir: str = "var/config", crash_logger: Optional[StructuredCrashLogger] = None):
        self.config_dir = os.path.abspath(config_dir)
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "startup.json")
        self.crash_logger = crash_logger or StructuredCrashLogger()
        self.os_type: str = sys.platform
        self.is_registered: bool = False
        self._init_config()

    def _init_config(self):
        """Initialize or load startup configuration file."""
        if not os.path.exists(self.config_file):
            default_config = {
                "os_type": self.os_type,
                "auto_start_on_boot": True,
                "start_tray": True,
                "start_voice_listener": False,
                "interval_seconds": 60,
                "registered_at": time.time(),
            }
            try:
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dumps(default_config, indent=2)
            except Exception:
                pass

    def detect_os(self) -> Dict[str, Any]:
        """Detect operating system and return platform details."""
        return {
            "platform": sys.platform,
            "is_windows": sys.platform.startswith("win"),
            "python_version": sys.version.split()[0],
        }

    def register_windows_startup(self) -> Dict[str, Any]:
        """Register Alfred startup launcher on Windows."""
        is_win = sys.platform.startswith("win")
        startup_bat = os.path.join(self.config_dir, "alfred_startup.bat")

        try:
            with open(startup_bat, "w", encoding="utf-8") as f:
                f.write(f'@echo off\ncd /d "{os.getcwd()}"\npython -m jarvisx daemon --start\n')

            if is_win:
                appdata = os.environ.get("APPDATA", "")
                if appdata:
                    win_startup_folder = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup")
                    if os.path.exists(win_startup_folder):
                        win_bat = os.path.join(win_startup_folder, "AlfredOS.bat")
                        with open(win_bat, "w", encoding="utf-8") as f2:
                            f2.write(f'@echo off\ncd /d "{os.getcwd()}"\npython -m jarvisx daemon --start\n')

            self.is_registered = True
        except Exception as e:
            self.crash_logger.log_crash("startup_manager", str(e))
            self.is_registered = False

        status_str = "REGISTERED" if self.is_registered else "BYPASS"
        self.crash_logger.log_startup({"registered": self.is_registered, "path": startup_bat})

        return {
            "status": status_str,
            "platform": sys.platform,
            "is_registered": self.is_registered,
            "startup_script": startup_bat,
        }

    def validate_startup_config(self) -> Dict[str, Any]:
        """Validate startup configuration and folder permissions."""
        os_info = self.detect_os()
        dirs = ["var/logs", "var/db", "var/downloads", "var/deliverables"]
        accessible = True
        for d in dirs:
            os.makedirs(os.path.abspath(d), exist_ok=True)
            if not os.access(os.path.abspath(d), os.W_OK):
                accessible = False

        return {
            "valid": accessible,
            "status": "VALIDATED" if accessible else "INVALID",
            "os_info": os_info,
            "config_file": self.config_file,
        }
