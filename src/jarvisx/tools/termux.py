import subprocess
from typing import Any, Optional

from jarvisx.core.health import HealthStatus
from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool, ToolResult


class TermuxTool(BaseTool):
    """Interfaces with Termux:API on Android devices."""
    name = "termux"

    def __init__(self, logger: Optional[StructuredLogger] = None):
        self.logger = logger or StructuredLogger()

    def _run_termux_command(self, cmd: list[str]) -> ToolResult:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return ToolResult(success=True, message=f"Executed {' '.join(cmd)}", data={"output": result.stdout})
        except subprocess.CalledProcessError as e:
            self.logger.write("error", "termux.command.failed", cmd=cmd, error=e.stderr)
            return ToolResult(success=False, message=f"Termux API failed: {e.stderr}")
        except FileNotFoundError:
            # Termux:API is not installed or not running in Termux
            self.logger.write("warning", "termux.not_found")
            return ToolResult(success=False, message="Termux API is not available on this environment. Offline/Simulation mode.")

    def notify(self, title: str, content: str) -> ToolResult:
        """Shows a system notification."""
        return self._run_termux_command(["termux-notification", "--title", title, "--content", content])

    def vibrate(self, duration_ms: int = 500) -> ToolResult:
        """Vibrates the device."""
        return self._run_termux_command(["termux-vibrate", "-d", str(duration_ms)])

    def set_clipboard(self, text: str) -> ToolResult:
        """Sets the device clipboard."""
        # Using stdin for text
        try:
            result = subprocess.run(["termux-clipboard-set"], input=text, capture_output=True, text=True, check=True)
            return ToolResult(success=True, message="Clipboard updated.")
        except Exception as e:
            return ToolResult(success=False, message=f"Clipboard set failed: {e}")

    def battery_status(self) -> ToolResult:
        """Gets battery status."""
        return self._run_termux_command(["termux-battery-status"])

    def trigger_macrodroid(self, webhook_id: str) -> ToolResult:
        """Triggers a MacroDroid macro via its local webhook or intent."""
        # This can be done via termux-intent or curl to a local MacroDroid HTTP server
        # For offline execution, termux-intent is best:
        # am broadcast -a com.arlosoft.macrodroid.MACRO_ACTION -e name "MacroName"
        # Termux equivalent wrapper:
        cmd = [
            "termux-open", 
            f"macrodroid://webhook?id={webhook_id}"
        ]
        return self._run_termux_command(cmd)

    def health(self) -> HealthStatus:
        # Check if termux-battery-status exists as a proxy for Termux:API
        try:
            subprocess.run(["termux-battery-status"], capture_output=True, check=True)
            return HealthStatus.ok("Termux API is available.")
        except Exception:
            return HealthStatus.fail("Termux API is not available in this environment.")
