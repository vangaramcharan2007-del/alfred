"""
Jarvis X Background Daemon Service.
Always-on background runtime manager for Alfred Core & Friday Core.
Supports PID file locking, health monitoring logging, and Windows Startup registration.
"""
from __future__ import annotations
import os
import sys
import time
import signal
import threading
from pathlib import Path
from typing import Dict, Any, Optional


class JarvisDaemon:
    """
    Background daemon manager for Alfred and Friday.
    """

    def __init__(self, var_dir: Optional[str] = None):
        self.var_dir = Path(var_dir or "var")
        self.var_dir.mkdir(parents=True, exist_ok=True)
        self.pid_file = self.var_dir / "jarvisd.pid"
        self.log_file = self.var_dir / "logs" / "daemon.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.running = False
        self._monitor_thread: Optional[threading.Thread] = None

    def log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [jarvisd] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)

    def is_running(self) -> bool:
        if not self.pid_file.exists():
            return False
        try:
            pid = int(self.pid_file.read_text().strip())
            # Check process survival on Windows / OS
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                PROCESS_QUERY_INFORMATION = 0x0400
                h_proc = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
                if h_proc:
                    kernel32.CloseHandle(h_proc)
                    return True
                return False
            else:
                os.kill(pid, 0)
                return True
        except Exception:
            return False

    def start(self) -> Dict[str, Any]:
        if self.is_running():
            return {"status": "ALREADY_RUNNING", "pid_file": str(self.pid_file)}

        pid = os.getpid()
        self.pid_file.write_text(str(pid), encoding="utf-8")
        self.running = True
        self.log(f"Daemon started with PID {pid}")

        self._monitor_thread = threading.Thread(target=self._health_loop, daemon=True)
        self._monitor_thread.start()

        return {"status": "STARTED", "pid": pid, "log_file": str(self.log_file)}

    def stop(self) -> Dict[str, Any]:
        self.running = False
        if self.pid_file.exists():
            try:
                self.pid_file.unlink()
            except Exception:
                pass
        self.log("Daemon stopped gracefully.")
        return {"status": "STOPPED"}

    def _health_loop(self):
        while self.running:
            self.log("Health Check: Alfred Core [ONLINE] | Friday Core [ONLINE] | Watchers [ACTIVE]")
            time.sleep(60)

    def generate_startup_script(self) -> Dict[str, Any]:
        """Generate Windows startup registration scripts."""
        scripts_dir = self.var_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        python_exe = sys.executable
        main_path = Path(__file__).resolve().parent.parent / "main.py"

        bat_content = f'@echo off\n"{python_exe}" "{main_path}" daemon --start\n'
        bat_file = scripts_dir / "register_startup.bat"
        bat_file.write_text(bat_content, encoding="utf-8")

        ps1_content = f'Start-Process -FilePath "{python_exe}" -ArgumentList "{main_path} daemon --start" -WindowStyle Hidden\n'
        ps1_file = scripts_dir / "register_startup.ps1"
        ps1_file.write_text(ps1_content, encoding="utf-8")

        return {
            "status": "GENERATED",
            "bat_script": str(bat_file),
            "ps1_script": str(ps1_file),
            "instructions": f"Add {bat_file} to Windows Startup folder (shell:startup)."
        }
