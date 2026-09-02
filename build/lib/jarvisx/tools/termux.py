import os
import subprocess
from typing import Any, Optional

from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool, ToolResult


class TermuxTool(BaseTool):
    """Interfaces with Termux:API on Android devices via Tailscale ADB."""
    name = "termux"

    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or StructuredLogger()
        self.adb_target = os.environ.get("JARVIS_ADB_TARGET")

    def _run_termux_command(self, cmd: list[str]) -> ToolResult:
        if self.adb_target:
            # Route over ADB Bridge
            full_cmd = ["adb", "-s", self.adb_target, "shell"] + cmd
        else:
            full_cmd = cmd
            
        try:
            result = subprocess.run(full_cmd, capture_output=True, text=True, check=True)
            return ToolResult(success=True, message=f"Executed {' '.join(cmd)}", data={"output": result.stdout})
        except subprocess.CalledProcessError as e:
            self.logger.write("error", "termux.command.failed", cmd=full_cmd, error=e.stderr)
            return ToolResult(success=False, message=f"Termux API failed: {e.stderr}")
        except FileNotFoundError:
            self.logger.write("warning", "termux.not_found")
            return ToolResult(success=False, message="Termux API is not available on this environment. Offline/Simulation mode.")

    def notify(self, title: str, content: str) -> ToolResult:
        """Shows a system notification."""
        return self._run_termux_command(["termux-notification", "--title", f"'{title}'", "--content", f"'{content}'"])

    def vibrate(self, duration_ms: int = 500) -> ToolResult:
        """Vibrates the device."""
        return self._run_termux_command(["termux-vibrate", "-d", str(duration_ms)])

    def set_clipboard(self, text: str) -> ToolResult:
        """Sets the device clipboard."""
        if self.adb_target:
            full_cmd = ["adb", "-s", self.adb_target, "shell", "termux-clipboard-set"]
        else:
            full_cmd = ["termux-clipboard-set"]
        try:
            result = subprocess.run(full_cmd, input=text, capture_output=True, text=True, check=True)
            return ToolResult(success=True, message="Clipboard updated.")
        except Exception as e:
            return ToolResult(success=False, message=f"Clipboard set failed: {e}")

    def battery_status(self) -> ToolResult:
        """Gets battery status."""
        return self._run_termux_command(["termux-battery-status"])
        
    def speak(self, text: str) -> ToolResult:
        """Speaks out loud on the phone."""
        return self._run_termux_command(["termux-tts-speak", f"'{text}'"])
        
    def read_sms(self, limit: int = 5) -> ToolResult:
        """Reads latest SMS messages."""
        return self._run_termux_command(["termux-sms-list", "-l", str(limit)])
        
    def send_sms(self, number: str, text: str) -> ToolResult:
        """Sends an SMS."""
        return self._run_termux_command(["termux-sms-send", "-n", number, f"'{text}'"])

    def trigger_macrodroid(self, webhook_id: str) -> ToolResult:
        cmd = ["termux-open", f"macrodroid://webhook?id={webhook_id}"]
        return self._run_termux_command(cmd)

    def health(self) -> HealthStatus:
        if self.adb_target:
            return HealthStatus.ok(f"ADB Bridge targeted at {self.adb_target}")
        try:
            subprocess.run(["termux-battery-status"], capture_output=True, check=True)
            return HealthStatus.ok("Termux API is available locally.")
        except Exception:
            return HealthStatus.fail("Termux API is not available.")
