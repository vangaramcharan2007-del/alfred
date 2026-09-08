"""
Live Chrome Profile CDP Connector for Jarvis X.
Enables attaching to real user Chrome sessions with active logins, cookies,
and persistent credentials over the Chrome DevTools Protocol (port 9222).
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.chrome_cdp")


class ChromeCDPBridge:
    """Manages Chrome discovery, remote debugging port health, and profile binding."""

    DEFAULT_PORT = 9222

    @staticmethod
    def find_chrome_executable() -> Optional[str]:
        """Locates standard Google Chrome binary path on Windows."""
        candidates = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return path
        return None

    @staticmethod
    def get_default_user_data_dir() -> Path:
        """Returns the default Chrome user data directory path."""
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            return Path(local_app_data) / "Google" / "Chrome" / "User Data"
        return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"

    @classmethod
    def probe_cdp_status(cls, port: int = DEFAULT_PORT, timeout_sec: float = 1.0) -> Dict[str, Any]:
        """Probes http://127.0.0.1:{port}/json/version to inspect remote debugging readiness."""
        url = f"http://127.0.0.1:{port}/json/version"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "JarvisX-CDP-Probe"})
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return {
                        "active": True,
                        "port": port,
                        "browser": data.get("Browser", "Chrome"),
                        "protocol_version": data.get("Protocol-Version", "1.3"),
                        "webSocketDebuggerUrl": data.get("webSocketDebuggerUrl", ""),
                    }
        except Exception:
            pass
        return {"active": False, "port": port, "browser": None, "webSocketDebuggerUrl": None}

    @classmethod
    def get_cdp_url(cls, port: int = DEFAULT_PORT) -> str:
        return f"http://127.0.0.1:{port}"

    @classmethod
    def launch_debug_chrome(
        cls,
        port: int = DEFAULT_PORT,
        user_data_dir: Optional[str] = None,
        additional_args: Optional[List[str]] = None,
    ) -> Optional[subprocess.Popen]:
        """Spawns Chrome with remote debugging enabled."""
        chrome_exe = cls.find_chrome_executable()
        if not chrome_exe:
            logger.error("[ChromeCDP] Chrome executable not found on system.")
            return None

        status = cls.probe_cdp_status(port)
        if status["active"]:
            logger.info(f"[ChromeCDP] Chrome is already running with CDP on port {port}.")
            return None

        cmd = [
            chrome_exe,
            f"--remote-debugging-port={port}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        if user_data_dir:
            cmd.append(f"--user-data-dir={user_data_dir}")

        if additional_args:
            cmd.extend(additional_args)

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
            )
            # Wait up to 4s for CDP endpoint to become ready
            t0 = time.time()
            while time.time() - t0 < 4.0:
                if cls.probe_cdp_status(port)["active"]:
                    logger.info(f"[ChromeCDP] Debug Chrome launched successfully on port {port}.")
                    return proc
                time.sleep(0.2)
            logger.warning("[ChromeCDP] Chrome process started, but CDP endpoint timed out.")
            return proc
        except Exception as e:
            logger.error(f"[ChromeCDP] Failed to launch debug Chrome: {e}")
            return None
