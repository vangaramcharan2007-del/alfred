"""Built-in Tool Implementations for Tool Kernel.

Six initial tools: get_current_time, get_system_info, list_directory,
read_file, create_file, open_app.
"""

from __future__ import annotations

import datetime
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from jarvisx.tools.tool_kernel import (
    PermissionLevel,
    Tool,
    ToolResult,
    ToolSpec,
)


# ---------------------------------------------------------------------------
# Path safety helpers (reuse SandboxGuardrails)
# ---------------------------------------------------------------------------

_BLOCKED_SYSTEM_DIRS = {
    "c:\\windows", "c:\\program files", "c:\\program files (x86)",
    "c:\\programdata", "c:\\$recycle.bin", "c:\\system volume information",
}


def _is_system_path(p: str) -> bool:
    resolved = str(Path(p).resolve()).lower()
    return any(resolved.startswith(d) for d in _BLOCKED_SYSTEM_DIRS)


def _validate_path(p: str) -> Dict[str, Any]:
    """Validate a path using SandboxGuardrails."""
    from jarvisx.security.sandbox_guardrails import SandboxGuardrails
    guardrails = SandboxGuardrails(allowed_workspace=".")
    return guardrails.validate_file_path(p)


# ---------------------------------------------------------------------------
# Tool: get_current_time
# ---------------------------------------------------------------------------

class GetCurrentTimeTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="get_current_time",
            description="Returns the current local system date and time.",
            input_schema={"type": "object", "properties": {}, "required": []},
            permission_level=PermissionLevel.SAFE,
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        now = datetime.datetime.now()
        return ToolResult(
            status="success",
            tool="get_current_time",
            result={
                "time": now.strftime("%I:%M:%S %p"),
                "date": now.strftime("%A, %B %d, %Y"),
                "iso": now.isoformat(),
            },
        )

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: get_system_info
# ---------------------------------------------------------------------------

class GetSystemInfoTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="get_system_info",
            description="Returns safe system information: OS, CPU, RAM, disk, GPU summary.",
            input_schema={"type": "object", "properties": {}, "required": []},
            permission_level=PermissionLevel.SAFE,
            required_scope="filesystem.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        import shutil
        info: Dict[str, Any] = {
            "os": f"{platform.system()} {platform.release()} ({platform.version()})",
            "cpu": platform.processor() or "Unknown",
            "architecture": platform.machine(),
            "python": platform.python_version(),
        }
        # RAM
        try:
            import psutil
            mem = psutil.virtual_memory()
            info["ram_total_gb"] = round(mem.total / (1024 ** 3), 2)
            info["ram_available_gb"] = round(mem.available / (1024 ** 3), 2)
            info["ram_percent_used"] = mem.percent
        except ImportError:
            info["ram"] = "psutil not available"
        # Disk
        try:
            disk = shutil.disk_usage(".")
            info["disk_total_gb"] = round(disk.total / (1024 ** 3), 2)
            info["disk_free_gb"] = round(disk.free / (1024 ** 3), 2)
        except Exception:
            info["disk"] = "unavailable"
        # GPU (safe summary)
        try:
            if sys.platform == "win32":
                r = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True, text=True, timeout=5,
                )
                gpus = [line.strip() for line in r.stdout.strip().split("\n") if line.strip() and line.strip() != "Name"]
                info["gpu"] = gpus if gpus else ["Unknown"]
        except Exception:
            info["gpu"] = ["query failed"]

        return ToolResult(status="success", tool="get_system_info", result=info)

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and isinstance(result.result, dict) and "os" in result.result
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: list_directory
# ---------------------------------------------------------------------------

class ListDirectoryTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="list_directory",
            description="Lists files and directories at the given path.",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Directory path to list."}},
                "required": ["path"],
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="filesystem.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        target = arguments.get("path", ".")
        path = Path(target)

        if not path.exists():
            return ToolResult(status="failed", tool="list_directory", error=f"Path does not exist: '{target}'")
        if not path.is_dir():
            return ToolResult(status="failed", tool="list_directory", error=f"Path is not a directory: '{target}'")

        entries = []
        try:
            for entry in sorted(path.iterdir()):
                entries.append({
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else None,
                })
        except PermissionError:
            return ToolResult(status="failed", tool="list_directory", error=f"Permission denied: '{target}'")

        return ToolResult(status="success", tool="list_directory", result={"path": str(path.resolve()), "count": len(entries), "entries": entries[:100]})

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        target = arguments.get("path", ".")
        verified = result.status == "success" and Path(target).exists()
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: read_file
# ---------------------------------------------------------------------------

_MAX_READ_BYTES = 1_048_576  # 1 MB

class ReadFileTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="read_file",
            description="Reads the text contents of a file (max 1 MB).",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path to read."}},
                "required": ["path"],
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="filesystem.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        target = arguments.get("path", "")
        path = Path(target)

        if not path.exists():
            return ToolResult(status="failed", tool="read_file", error=f"File does not exist: '{target}'")
        if not path.is_file():
            return ToolResult(status="failed", tool="read_file", error=f"Path is not a file: '{target}'")
        if path.stat().st_size > _MAX_READ_BYTES:
            return ToolResult(status="failed", tool="read_file", error=f"File too large ({path.stat().st_size} bytes > {_MAX_READ_BYTES} limit)")

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return ToolResult(status="failed", tool="read_file", error=f"Read error: {e}")

        return ToolResult(status="success", tool="read_file", result={"path": str(path.resolve()), "size": len(content), "content": content})

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and isinstance(result.result, dict) and bool(result.result.get("content"))
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: create_file
# ---------------------------------------------------------------------------

class CreateFileTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="create_file",
            description="Creates a new file with the specified content. Requires user confirmation.",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to create."},
                    "content": {"type": "string", "description": "Text content to write."},
                },
                "required": ["path", "content"],
            },
            permission_level=PermissionLevel.CONFIRM,
            required_scope="filesystem.write(project_only)",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        target = arguments.get("path", "")
        content = arguments.get("content", "")
        path = Path(target)

        # Block system-critical locations
        if _is_system_path(target):
            return ToolResult(status="failed", tool="create_file", error=f"Blocked: cannot write to system location '{target}'")

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            return ToolResult(status="failed", tool="create_file", error=f"Write error: {e}")

        return ToolResult(status="success", tool="create_file", result={"path": str(path.resolve()), "size": len(content)})

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        target = arguments.get("path", "")
        path = Path(target)
        verified = result.status == "success" and path.exists() and path.is_file()
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: open_app
# ---------------------------------------------------------------------------

class OpenAppTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="open_app",
            description="Opens an application by name using the safe allowlisted launcher.",
            input_schema={
                "type": "object",
                "properties": {"application": {"type": "string", "description": "Application name to open."}},
                "required": ["application"],
            },
            permission_level=PermissionLevel.SAFE,
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        app_name = arguments.get("application", "")
        if not app_name:
            return ToolResult(status="failed", tool="open_app", error="Empty application name")

        try:
            from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
            orch = DynamicOrchestrator()
            res = orch.find_and_launch_app(app_name)
            valid_statuses = ("LAUNCHED_LOCAL", "LAUNCHED_WEB", "LAUNCHED_WEB_DIRECT", "LAUNCHED_DESKTOP", "SEARCHED_WEB")
            status = "success" if res.get("status") in valid_statuses else "failed"
            return ToolResult(status=status, tool="open_app", result=res)
        except Exception as e:
            return ToolResult(status="failed", tool="open_app", error=f"Launch error: {e}")

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        valid_statuses = ("LAUNCHED_LOCAL", "LAUNCHED_WEB", "LAUNCHED_WEB_DIRECT", "LAUNCHED_DESKTOP", "SEARCHED_WEB")
        verified = result.status == "success" and bool(result.result) and result.result.get("status") in valid_statuses
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: capture_screen
# ---------------------------------------------------------------------------

class CaptureScreenTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="capture_screen",
            description="Captures the desktop screen and returns structured UI elements, open windows, and active window.",
            input_schema={"type": "object", "properties": {}, "required": []},
            permission_level=PermissionLevel.SAFE,
            required_scope="desktop.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        try:
            from jarvisx.vision.ui_detector import UIDetector
            detector = UIDetector()
            ui_state = detector.scan_ui_state()
            return ToolResult(
                status="success",
                tool="capture_screen",
                result={
                    "active_window": ui_state.focused_window or "Desktop",
                    "width": ui_state.screen_resolution[0],
                    "height": ui_state.screen_resolution[1],
                    "window_count": len(ui_state.windows),
                    "windows": [w.to_dict() for w in ui_state.windows],
                    "element_count": len(ui_state.elements),
                    "elements": [
                        {
                            "label": el.label,
                            "type": el.type,
                            "bounds": list(el.bounding_box),
                            "center": list(el.center_coordinates),
                        }
                        for el in ui_state.elements[:15]
                    ],
                },
            )
        except Exception as e:
            return ToolResult(status="failed", tool="capture_screen", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result) and result.result.get("width", 0) > 0
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: get_active_window
# ---------------------------------------------------------------------------

class GetActiveWindowTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="get_active_window",
            description="Returns the currently focused/active desktop window title and process name.",
            input_schema={"type": "object", "properties": {}, "required": []},
            permission_level=PermissionLevel.SAFE,
            required_scope="desktop.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        try:
            from jarvisx.vision.ui_detector import UIDetector
            detector = UIDetector()
            ui_state = detector.scan_ui_state()
            active_win = ui_state.windows[0] if ui_state.windows else None
            return ToolResult(
                status="success",
                tool="get_active_window",
                result={
                    "title": active_win.title if active_win else (ui_state.focused_window or "Desktop"),
                    "process_name": active_win.process_name if active_win else "explorer",
                    "is_active": True,
                    "size": active_win.size if active_win else (1920, 1080),
                },
            )
        except Exception as e:
            return ToolResult(status="failed", tool="get_active_window", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result) and bool(result.result.get("title"))
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: list_windows
# ---------------------------------------------------------------------------

class ListWindowsTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="list_windows",
            description="Lists open application windows on the desktop.",
            input_schema={"type": "object", "properties": {}, "required": []},
            permission_level=PermissionLevel.SAFE,
            required_scope="desktop.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        try:
            from jarvisx.vision.ui_detector import UIDetector
            detector = UIDetector()
            ui_state = detector.scan_ui_state()
            return ToolResult(
                status="success",
                tool="list_windows",
                result={
                    "count": len(ui_state.windows),
                    "windows": [w.to_dict() for w in ui_state.windows],
                },
            )
        except Exception as e:
            return ToolResult(status="failed", tool="list_windows", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and isinstance(result.result, dict) and "windows" in result.result
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: click
# ---------------------------------------------------------------------------

class ClickTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="click",
            description="Clicks at the specified screen coordinates (x, y) after safety validation. Requires user confirmation.",
            input_schema={
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X pixel coordinate."},
                    "y": {"type": "integer", "description": "Y pixel coordinate."},
                    "button": {"type": "string", "enum": ["left", "right", "middle"], "default": "left"},
                },
                "required": ["x", "y"],
            },
            permission_level=PermissionLevel.CONFIRM,
            required_scope="desktop.write",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        x = arguments.get("x")
        y = arguments.get("y")
        button = arguments.get("button", "left")

        if not isinstance(x, int) or not isinstance(y, int):
            return ToolResult(status="failed", tool="click", error="Coordinates x and y must be integers.")

        try:
            from jarvisx.vision.action_validator import ActionSafetyValidator
            from jarvisx.vision.mouse_controller import MouseController
            from jarvisx.vision.ui_detector import UIDetector

            detector = UIDetector()
            ui_state = detector.scan_ui_state()
            active_window = ui_state.focused_window or ""

            validator = ActionSafetyValidator()
            val_res = validator.validate_mouse_action("click", (x, y), active_window=active_window)
            if val_res["decision"] == "BLOCK":
                return ToolResult(status="failed", tool="click", error=val_res["reason"])

            controller = MouseController()
            click_res = controller.click(x=x, y=y, button=button)
            return ToolResult(status="success", tool="click", result=click_res)
        except Exception as e:
            return ToolResult(status="failed", tool="click", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: type_text
# ---------------------------------------------------------------------------

class TypeTextTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="type_text",
            description="Types text into the active desktop window after safety validation. Requires user confirmation.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type into active window."}
                },
                "required": ["text"],
            },
            permission_level=PermissionLevel.CONFIRM,
            required_scope="desktop.write",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        text = arguments.get("text", "")
        if not isinstance(text, str) or not text:
            return ToolResult(status="failed", tool="type_text", error="Text must be a non-empty string.")

        try:
            from jarvisx.vision.action_validator import ActionSafetyValidator
            from jarvisx.vision.keyboard_controller import KeyboardController
            from jarvisx.vision.ui_detector import UIDetector

            detector = UIDetector()
            ui_state = detector.scan_ui_state()
            active_window = ui_state.focused_window or ""

            validator = ActionSafetyValidator()
            val_res = validator.validate_keyboard_action(text, active_window=active_window)
            if val_res["decision"] == "BLOCK":
                return ToolResult(status="failed", tool="type_text", error=val_res["reason"])

            controller = KeyboardController()
            type_res = controller.type_text(text)
            return ToolResult(status="success", tool="type_text", result=type_res)
        except Exception as e:
            return ToolResult(status="failed", tool="type_text", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result) and result.result.get("characters_typed", 0) > 0
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: press_key
# ---------------------------------------------------------------------------

class PressKeyTool(Tool):
    ALLOWED_KEYS = {
        "enter", "esc", "tab", "backspace", "delete", "up", "down", "left", "right",
        "space", "home", "end", "pageup", "pagedown", "f1", "f2", "f3", "f4", "f5",
        "ctrl+s", "ctrl+c", "ctrl+v", "ctrl+z", "ctrl+a", "alt+tab"
    }

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="press_key",
            description="Presses a keyboard key in the active window. Requires user confirmation.",
            input_schema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key name to press (e.g. 'enter', 'tab', 'esc', 'ctrl+s')."}
                },
                "required": ["key"],
            },
            permission_level=PermissionLevel.CONFIRM,
            required_scope="desktop.write",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        key = str(arguments.get("key", "")).lower().strip()
        if not key or key not in self.ALLOWED_KEYS:
            return ToolResult(status="failed", tool="press_key", error=f"Key '{key}' is not in the allowed safe keys set.")

        try:
            from jarvisx.vision.keyboard_controller import KeyboardController
            controller = KeyboardController()
            if "+" in key:
                keys = [k.strip() for k in key.split("+")]
                res = controller.press_hotkey(*keys)
            else:
                res = controller.press_key(key)
            return ToolResult(status="success", tool="press_key", result=res)
        except Exception as e:
            return ToolResult(status="failed", tool="press_key", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Registry bootstrap
# ---------------------------------------------------------------------------

def register_builtin_tools(registry: "ToolRegistry") -> None:
    """Register all built-in tools into the given registry."""
    from jarvisx.tools.tool_kernel import ToolRegistry as _TR
    registry.register(GetCurrentTimeTool())
    registry.register(GetSystemInfoTool())
    registry.register(ListDirectoryTool())
    registry.register(ReadFileTool())
    registry.register(CreateFileTool())
    registry.register(OpenAppTool())
    registry.register(CaptureScreenTool())
    registry.register(GetActiveWindowTool())
    registry.register(ListWindowsTool())
    registry.register(ClickTool())
    registry.register(TypeTextTool())
    registry.register(PressKeyTool())

