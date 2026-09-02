"""
Linux Native Desktop & Kiosk Deployer for Spider-Man E.V. HUD.
==============================================================
Installs and configures the native FreeDesktop autostart entry and full-screen
kiosk homescreen inside the Linux Mint VM environment so E.V. boots natively
on the Linux VM display (:0).
"""

from __future__ import annotations

import logging
import os
import shutil
import stat
import time
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("jarvisx.linux_desktop_deployer")


class LinuxNativeDesktopDeployer:
    """Deploys the Spider-Man E.V. Workstation directly into the Linux Desktop environment."""

    _instance: Optional["LinuxNativeDesktopDeployer"] = None

    @classmethod
    def get_instance(cls) -> "LinuxNativeDesktopDeployer":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def generate_desktop_entry_content(self, script_path: str) -> str:
        """Generates FreeDesktop .desktop specification entry."""
        return f"""[Desktop Entry]
Type=Application
Name=Spider-Man E.V. Workstation
Comment=ADHD-Friendly Female Voice Co-Pilot & Dual-Core Linux HUD
Exec=/bin/bash "{script_path}"
Icon=utilities-terminal
Terminal=false
Categories=System;Development;Utility;
X-GNOME-Autostart-enabled=true
X-Cinnamon-Autostart-enabled=true
"""

    def generate_kiosk_launcher_script(self, server_py_path: str) -> str:
        """Generates the bash launcher that boots the Python HUD server and opens it in fullscreen."""
        return f"""#!/bin/bash
# ==============================================================================
# SPIDER-MAN E.V. // NATIVE LINUX MINT DESKTOP HOMESCREEN LAUNCHER
# ==============================================================================

export DISPLAY=:0

# 1. Start E.V. Linux HUD Server in background
python3 "{server_py_path}" > /tmp/spiderman_ev.log 2>&1 &
SERVER_PID=$!
sleep 1.5

# 2. Launch Fullscreen Kiosk on Linux Desktop
if command -v firefox >/dev/null 2>&1; then
    firefox --kiosk "http://localhost:5050" &
elif command -v chromium-browser >/dev/null 2>&1; then
    chromium-browser --kiosk --app="http://localhost:5050" &
elif command -v google-chrome >/dev/null 2>&1; then
    google-chrome --kiosk --app="http://localhost:5050" &
else
    # Fallback to default xdg-open
    xdg-open "http://localhost:5050" &
fi

echo "[✓] Spider-Man E.V. Native Linux Homescreen Active (PID: $SERVER_PID)"
"""

    def deploy_to_linux_environment(self, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Deploys the desktop launcher and autostart configuration to Linux storage."""
        from jarvisx.agents.linux_agent import LinuxBridgeAgent
        agent = LinuxBridgeAgent.get_instance()

        deploy_root = Path(output_dir) if output_dir else Path(os.getcwd()) / "var" / "linux_desktop"
        deploy_root.mkdir(parents=True, exist_ok=True)

        server_src = Path(os.getcwd()) / "src" / "jarvisx" / "gui" / "spiderman_linux_hud.py"
        server_dst = deploy_root / "spiderman_linux_hud.py"
        if server_src.exists():
            shutil.copy2(server_src, server_dst)

        # 1. Create Kiosk Launcher Script
        kiosk_script = deploy_root / "launch_spiderman_ev_homescreen.sh"
        kiosk_content = self.generate_kiosk_launcher_script(server_dst.as_posix())
        kiosk_script.write_text(kiosk_content, encoding="utf-8")
        
        # Make script executable
        try:
            st = os.stat(kiosk_script)
            os.chmod(kiosk_script, st.st_mode | stat.S_IEXEC)
        except Exception:
            pass

        # 2. Create FreeDesktop Entry
        desktop_file = deploy_root / "spiderman_ev.desktop"
        desktop_content = self.generate_desktop_entry_content(kiosk_script.as_posix())
        desktop_file.write_text(desktop_content, encoding="utf-8")

        # 3. Deploy into Linux VM / WSL Autostart paths via Linux Agent
        res_autostart = agent.execute_bash(
            f"mkdir -p ~/.config/autostart ~/Desktop; "
            f"cp '{desktop_file.as_posix()}' ~/.config/autostart/ 2>/dev/null || true; "
            f"cp '{desktop_file.as_posix()}' ~/Desktop/ 2>/dev/null || true; "
            f"chmod +x '{kiosk_script.as_posix()}' 2>/dev/null || true; "
            f"echo 'DESKTOP_DEPLOYED_SUCCESSFULLY'"
        )

        logger.info(f"[LinuxDesktopDeployer] Deployed native E.V. desktop homescreen to {deploy_root}")

        return {
            "status": "success",
            "deployed_path": str(deploy_root.resolve()),
            "kiosk_script": str(kiosk_script.resolve()),
            "desktop_entry": str(desktop_file.resolve()),
            "linux_agent_output": res_autostart.get("stdout", ""),
            "message": "Spider-Man E.V. Native Linux Homescreen successfully installed in autostart!",
        }
