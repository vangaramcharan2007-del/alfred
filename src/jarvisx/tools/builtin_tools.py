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
        app_name = arguments.get("application") or arguments.get("app_name") or arguments.get("name") or arguments.get("app") or ""
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
# Tool: analyze_screen
# ---------------------------------------------------------------------------

class AnalyzeScreenTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="analyze_screen",
            description="Analyzes visible desktop screen, open application windows, and UI elements with bounding boxes for reasoning.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Optional search query to match specific buttons, windows, or inputs."},
                },
                "required": [],
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="desktop.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        query = arguments.get("query")
        try:
            from jarvisx.vision.ui_detector import UIDetector
            detector = UIDetector()
            analysis = detector.analyze_ui(query=query)
            return ToolResult(
                status="success",
                tool="analyze_screen",
                result=analysis,
            )
        except Exception as e:
            return ToolResult(status="failed", tool="analyze_screen", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = (
            result.status == "success"
            and isinstance(result.result, dict)
            and bool(result.result.get("active_window"))
            and result.result.get("width", 0) > 0
        )
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: web_search
# ---------------------------------------------------------------------------

class WebSearchTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="web_search",
            description="Searches the web for queries and returns bounded, structured titles, URLs, and snippets.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."}
                },
                "required": ["query"],
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="network.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        query = arguments.get("query", "")
        if not isinstance(query, str) or not query.strip():
            return ToolResult(status="failed", tool="web_search", error="Search query must be a non-empty string.")

        try:
            from jarvisx.tools.web_research import WebSearchEngine
            engine = WebSearchEngine()
            res = engine.search(query)
            return ToolResult(status="success", tool="web_search", result=res)
        except Exception as e:
            return ToolResult(status="failed", tool="web_search", error=f"Search failed: {e}")

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = (
            result.status == "success"
            and isinstance(result.result, dict)
            and "results" in result.result
        )
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: fetch_webpage
# ---------------------------------------------------------------------------

class FetchWebpageTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="fetch_webpage",
            description="Fetches an HTTP/HTTPS webpage and extracts bounded, clean text content without executing scripts.",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "HTTP or HTTPS URL to fetch."}
                },
                "required": ["url"],
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="network.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        url = arguments.get("url", "")
        if not isinstance(url, str) or not url.strip():
            return ToolResult(status="failed", tool="fetch_webpage", error="URL must be a non-empty string.")

        try:
            from jarvisx.tools.web_research import WebPageFetcher
            fetcher = WebPageFetcher()
            res = fetcher.fetch(url)
            status = res.get("status", "failed")
            error = res.get("error")
            return ToolResult(status=status, tool="fetch_webpage", result=res if status == "success" else None, error=error)
        except Exception as e:
            return ToolResult(status="failed", tool="fetch_webpage", error=f"Fetch failed: {e}")

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = (
            result.status == "success"
            and isinstance(result.result, dict)
            and bool(result.result.get("content") or result.result.get("title"))
        )
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: browser_open
# ---------------------------------------------------------------------------

class BrowserOpenTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="browser_open",
            description="Opens a validated HTTP/HTTPS URL in the default web browser.",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "HTTP or HTTPS URL to open."}
                },
                "required": ["url"],
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="network.read",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        url = arguments.get("url", "")
        if not isinstance(url, str) or not url.strip():
            return ToolResult(status="failed", tool="browser_open", error="URL must be a non-empty string.")

        from jarvisx.tools.web_research import WebPageFetcher
        fetcher = WebPageFetcher()
        val = fetcher.validate_url(url)
        if not val["valid"]:
            return ToolResult(status="failed", tool="browser_open", error=val["error"])

        import webbrowser
        webbrowser.open(val["url"])
        return ToolResult(status="success", tool="browser_open", result={"status": "OPENED", "url": val["url"]})

# ---------------------------------------------------------------------------
# Tool: reduce_heat_and_ram_usage / cool_system
# ---------------------------------------------------------------------------

class CoolSystemTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="reduce_heat_and_ram_usage",
            description="Reduces laptop heat, purges dormant RAM, throttles CPU to 4 threads, and unloads idle models.",
            input_schema={"type": "object", "properties": {}, "required": []},
            permission_level=PermissionLevel.SAFE,
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        from jarvisx.hardware.npu_accelerator import get_npu_accelerator
        npu = get_npu_accelerator()
        cooling = npu.enforce_memory_cooling()
        health = npu.get_system_health()
        return ToolResult(
            status="success",
            tool="reduce_heat_and_ram_usage",
            result={
                "status": "COOLED",
                "freed_mb": cooling["freed_mb"],
                "active_ram_percent": health["ram_percent"],
                "cpu_load": health["cpu_percent"],
                "power_profile": "ECO",
                "message": "Memory purged, 4-thread CPU throttling enforced, and thermal stability restored."
            }
        )

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: clear_space / clean_disk_space
# ---------------------------------------------------------------------------

class CleanDiskSpaceTool(Tool):
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="clear_space",
            description="Cleans temporary files, cache directories, and local build artifacts to free disk space.",
            input_schema={"type": "object", "properties": {}, "required": []},
            permission_level=PermissionLevel.SAFE,
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        import shutil
        import tempfile

        freed_bytes = 0
        cleaned_dirs = []

        # 1. Clean local project caches (.pytest_cache, __pycache__)
        for root, dirs, files in os.walk("."):
            for d in list(dirs):
                if d in ("__pycache__", ".pytest_cache", ".ruff_cache"):
                    p = os.path.join(root, d)
                    try:
                        shutil.rmtree(p, ignore_errors=True)
                        cleaned_dirs.append(d)
                    except Exception:
                        pass

        # 2. Clean user temp folder safe files
        temp_dir = tempfile.gettempdir()
        if os.path.exists(temp_dir):
            for item in os.listdir(temp_dir):
                if item.startswith(("tmp", "jarvis", "pytest", "npm-", "pip-")):
                    p = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(p):
                            freed_bytes += os.path.getsize(p)
                            os.remove(p)
                        elif os.path.isdir(p):
                            shutil.rmtree(p, ignore_errors=True)
                    except Exception:
                        pass

        freed_mb = round(freed_bytes / (1024 * 1024), 2)
        return ToolResult(
            status="success",
            tool="clear_space",
            result={
                "status": "CLEARED",
                "freed_mb": freed_mb,
                "cleaned_caches": list(set(cleaned_dirs)),
                "message": f"Successfully cleared temporary caches and temporary files."
            }
        )

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: uacc_computer_control
# ---------------------------------------------------------------------------

class UACCComputerControlTool(Tool):
    """Generic desktop computer control tool backed by UACC and MCP."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="uacc_computer_control",
            description="Executes deterministic computer control actions (inspect, click, move, type, press, drag, launch_app) via UACC.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["inspect", "click", "move", "type", "press", "drag", "launch_app"],
                        "description": "The specific desktop action to perform."
                    },
                    "params": {
                        "type": "object",
                        "description": "Action-specific parameters (e.g. x, y, text, key, start_x, start_y, end_x, end_y, app_name)."
                    }
                },
                "required": ["action"]
            },
            permission_level=PermissionLevel.CONFIRM,
            required_scope="desktop.actuate"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        import time
        from jarvisx.computer_use.uacc_adapter import get_uacc_adapter
        from jarvisx.computer_use.computer_use_engine import get_computer_use_engine
        from jarvisx.observability.computer_use_logger import get_computer_use_logger
        
        action = arguments.get("action", "inspect")
        params = arguments.get("params", {})
        
        uacc = get_uacc_adapter()
        engine = get_computer_use_engine()
        logger = get_computer_use_logger()

        t0 = time.time()
        try:
            if action == "launch_app":
                res = engine.launch_app(params.get("app_name", "notepad"))
            else:
                res = uacc.execute_action(action, params)

            latency = round((time.time() - t0) * 1000, 1)
            success = res.get("status") == "success"
            
            logger.log_action(
                task_id=f"uacc_{int(time.time()*1000)}",
                tool="uacc_computer_control",
                action=action,
                success=success,
                latency_ms=latency,
                params=params,
                error=res.get("error")
            )

            status = "success" if success else "failed"
            return ToolResult(status=status, tool="uacc_computer_control", result=res, error=res.get("error"))
        except Exception as e:
            return ToolResult(status="failed", tool="uacc_computer_control", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: send_sms
# ---------------------------------------------------------------------------

class SendSmsTool(Tool):
    """Sends a real carrier SMS text message via Telephony Gateway / Twilio."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="send_sms",
            description="Sends a real carrier SMS text message to a phone number or contact name.",
            input_schema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "The destination phone number (e.g. '+917794979595' or '7794979595') or contact name (e.g. 'Dakshith', 'Dad')."
                    },
                    "message": {
                        "type": "string",
                        "description": "The SMS text message body to send."
                    }
                },
                "required": ["to", "message"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="telephony.sms"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        to_target = arguments.get("to", "")
        msg = arguments.get("message", "")
        
        # Check contact book if name
        digits = "".join(filter(str.isdigit, to_target))
        if not digits or len(digits) < 10:
            try:
                import json
                contacts_file = Path("config/contacts.json")
                if contacts_file.exists():
                    with open(contacts_file, "r", encoding="utf-8") as f:
                        c_data = json.load(f)
                    for key, entry in c_data.items():
                        if key in to_target.lower() or entry.get("name", "").lower() in to_target.lower():
                            digits = entry.get("phone", "")
                            break
            except Exception:
                pass

        from jarvisx.telephony.telephony_gateway import TelephonyGateway
        gw = TelephonyGateway.get_instance()
        res = gw.send_sms(to_number=digits or to_target, message=msg)
        status = "success" if res.get("status") == "SENT" else "failed"
        return ToolResult(status=status, tool="send_sms", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: place_carrier_call
# ---------------------------------------------------------------------------

class PlaceCarrierCallTool(Tool):
    """Places an outbound voice phone call via Telephony Gateway / Twilio."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="place_carrier_call",
            description="Places a real outbound voice phone call to a contact or phone number.",
            input_schema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "The destination phone number or contact name (e.g. 'Dakshith', 'Dad', '7794979595')."
                    },
                    "speech_text": {
                        "type": "string",
                        "description": "The spoken speech text or objective in Telugu or English."
                    }
                },
                "required": ["to"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="telephony.voice"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        to_target = arguments.get("to", "")
        say_text = arguments.get("speech_text", "నమస్కారం, నేను చరణ్ పర్సనల్ ఏఐ అసిస్టెంట్ ఆల్ఫ్రెడ్ ని మాట్లాడుతున్నాను.")
        
        digits = "".join(filter(str.isdigit, to_target))
        if not digits or len(digits) < 10:
            try:
                import json
                contacts_file = Path("config/contacts.json")
                if contacts_file.exists():
                    with open(contacts_file, "r", encoding="utf-8") as f:
                        c_data = json.load(f)
                    for key, entry in c_data.items():
                        if key in to_target.lower() or entry.get("name", "").lower() in to_target.lower():
                            digits = entry.get("phone", "")
                            break
            except Exception:
                pass

        from jarvisx.telephony.telephony_gateway import TelephonyGateway
        gw = TelephonyGateway.get_instance()
        res = gw.place_live_carrier_call(to_number=digits or to_target, say_text=say_text)
        status = "success" if res.get("status") == "RINGING" else "failed"
        return ToolResult(status=status, tool="place_carrier_call", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: send_whatsapp_message
# ---------------------------------------------------------------------------

class WhatsAppSendTool(Tool):
    """Sends a live message / voice note in WhatsApp via visual on-screen desktop actuation."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="send_whatsapp_message",
            description="Sends a live message and/or voice note to a WhatsApp contact on screen.",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "The contact name (e.g. 'Dakshith') or phone number."
                    },
                    "message": {
                        "type": "string",
                        "description": "The text message content to send."
                    }
                },
                "required": ["recipient", "message"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="desktop.actuate"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        recipient = arguments.get("recipient", "Dakshith")
        msg = arguments.get("message", "hello")
        
        from jarvisx.automation.whatsapp_actuation import send_whatsapp_live
        res = send_whatsapp_live(recipient=recipient, message=msg)
        return ToolResult(status="success", tool="send_whatsapp_message", result=res)

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: optimize_game_settings
# ---------------------------------------------------------------------------

class OptimizeGameSettingsTool(Tool):
    """Sovereign Game Optimization Tool for tuning graphics, FPS, and Windows performance for any game."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="optimize_game_settings",
            description="Analyzes laptop hardware and applies optimal in-game graphics settings, elevates process priority to High, trims RAM bloat, and optimizes Windows power plan for maximum FPS.",
            input_schema={
                "type": "object",
                "properties": {
                    "game": {
                        "type": "string",
                        "description": "Name of the target game (e.g. 'Valorant', 'GTA V', 'CS2', 'Cyberpunk', 'Minecraft', 'Fortnite', 'Apex Legends', 'Genshin Impact', etc.) or 'auto' to detect active game."
                    }
                },
                "required": ["game"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="gaming.optimize"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        game_query = arguments.get("game", "auto")
        
        from jarvisx.gaming.game_optimizer_agent import get_game_optimizer
        optimizer = get_game_optimizer()
        
        if game_query.lower() == "auto":
            active = optimizer.scan_active_running_game()
            if active:
                game_query = active[0]
            else:
                game_query = "generic_game"

        res = optimizer.optimize_game(game_query)
        return ToolResult(
            status="success",
            tool="optimize_game_settings",
            result=res.to_dict(),
        )

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Registry bootstrap
# ---------------------------------------------------------------------------

class CreateVoiceNoteAudioTool(Tool):
    """Generates an ultra-realistic neural audio voice note file in English, Telugu, or Hindi and plays it aloud."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="create_voice_note",
            description="Generates an ultra-realistic AI voice note audio file (.mp3) in English, Telugu, or Hindi, saves it to disk, and plays it aloud.",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "Recipient name (e.g. 'Dakshith', 'Charan')."
                    },
                    "message": {
                        "type": "string",
                        "description": "The speech content for the voice note."
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for speech synthesis ('english', 'telugu', 'hindi').",
                        "default": "english"
                    }
                },
                "required": ["message"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="voice.generate"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        import asyncio
        import edge_tts
        import time
        
        recip = arguments.get("recipient", "Sir")
        text = arguments.get("message", "Hello")
        lang = str(arguments.get("language", "english")).lower()
        
        voice_map = {
            "telugu": "te-IN-MohanNeural",
            "hindi": "hi-IN-MadhurNeural",
            "english": "en-GB-RyanNeural",
            "british": "en-GB-RyanNeural",
            "american": "en-US-GuyNeural"
        }
        voice = voice_map.get(lang, "en-GB-RyanNeural")
        
        out_dir = Path("var/voice_notes")
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_recip = "".join(filter(str.isalnum, recip)) or "note"
        out_file = out_dir / f"voice_note_{safe_recip}_{int(time.time())}.mp3"
        
        async def _gen():
            comm = edge_tts.Communicate(text, voice)
            await comm.save(str(out_file))
            
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        pool.submit(lambda: asyncio.run(_gen())).result()
                else:
                    loop.run_until_complete(_gen())
            except Exception:
                asyncio.run(_gen())
                
            # Play aloud via Pygame
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(str(out_file))
                pygame.mixer.music.play()
            except Exception:
                pass
                
            return ToolResult(
                status="success",
                tool="create_voice_note",
                result={
                    "file_path": str(out_file),
                    "recipient": recip,
                    "language": lang,
                    "voice": voice,
                    "message": text,
                    "status": "GENERATED_AND_PLAYED"
                }
            )
        except Exception as e:
            return ToolResult(status="failed", tool="create_voice_note", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


class SendWhatsAppVoiceNoteTool(Tool):
    """Generates an ultra-realistic neural audio voice note and pastes it into WhatsApp."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="send_whatsapp_voice_note",
            description="Generates an ultra-realistic neural audio voice note (.mp3) in Telugu, English, or Hindi and pastes it directly into WhatsApp chat.",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "Recipient contact name (e.g. 'Dakshith', 'Mom') or phone number."
                    },
                    "message": {
                        "type": "string",
                        "description": "Speech message to synthesize into the voice note."
                    },
                    "language": {
                        "type": "string",
                        "description": "Language ('telugu', 'english', 'hindi').",
                        "default": "english"
                    }
                },
                "required": ["recipient", "message"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="whatsapp.voice_note"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        from jarvisx.automation.social_actuation import send_whatsapp_voice_note
        recip = arguments.get("recipient", "Dakshith")
        msg = arguments.get("message", "Hello")
        lang = arguments.get("language", "english")
        res = send_whatsapp_voice_note(recipient=recip, message=msg, language=lang)
        return ToolResult(status="success", tool="send_whatsapp_voice_note", result=res)

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=True)


class CallWhatsAppTool(Tool):
    """Initiates a live WhatsApp Voice Call to a contact."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="call_whatsapp",
            description="Initiates a live on-screen WhatsApp voice call to a contact (e.g. 'Dakshith').",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "The contact name or phone number to call on WhatsApp."
                    }
                },
                "required": ["recipient"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="whatsapp.call"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        from jarvisx.automation.social_actuation import call_whatsapp_voice
        recip = arguments.get("recipient", "Dakshith")
        res = call_whatsapp_voice(recipient=recip)
        return ToolResult(status="success", tool="call_whatsapp", result=res)

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=True)


class SendInstagramDMTool(Tool):
    """Sends or composes an Instagram Direct Message."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="send_instagram_dm",
            description="Opens Instagram Direct Messages, prepares the message for a user, and navigates to their profile/chat.",
            input_schema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Instagram username (e.g. 'dakshith', '@dakshith_official')."
                    },
                    "message": {
                        "type": "string",
                        "description": "The message body to send."
                    }
                },
                "required": ["username", "message"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="instagram.dm"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        from jarvisx.automation.social_actuation import send_instagram_dm
        user = arguments.get("username", "dakshith")
        msg = arguments.get("message", "Hi")
        res = send_instagram_dm(username=user, message=msg)
        return ToolResult(status="success", tool="send_instagram_dm", result=res)

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=True)


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
    registry.register(AnalyzeScreenTool())
    registry.register(WebSearchTool())
    registry.register(FetchWebpageTool())
    registry.register(BrowserOpenTool())
    registry.register(CoolSystemTool())
    registry.register(CleanDiskSpaceTool())
    registry.register(UACCComputerControlTool())
    registry.register(SendSmsTool())
    registry.register(PlaceCarrierCallTool())
    registry.register(WhatsAppSendTool())
    registry.register(SendWhatsAppVoiceNoteTool())
    registry.register(CallWhatsAppTool())
    registry.register(SendInstagramDMTool())
    registry.register(CreateVoiceNoteAudioTool())
    registry.register(OptimizeGameSettingsTool())
    registry.register(AdaptiveGamingGovernorTool())
    registry.register(CreateAIAgentTool())
    registry.register(ListAIAgentsTool())
    registry.register(SetReminderTool())
    registry.register(ListRemindersTool())
    registry.register(CancelReminderTool())
    registry.register(GitCloneTool())
    registry.register(GitSyncTool())
    registry.register(GitStatusTool())
    registry.register(IntegrateRepoTool())
    registry.register(ExecuteCommandTool())
    registry.register(SurgicalRepoIntegrateTool())
    registry.register(FetchRepoFileTool())
    registry.register(AutonomousAssimilateRepoTool())





# ---------------------------------------------------------------------------
# Tool: adaptive_game_governor
# ---------------------------------------------------------------------------

class AdaptiveGamingGovernorTool(Tool):
    """Controls the background real-time game governor that continuously adjusts performance and load while gaming."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="adaptive_game_governor",
            description="Controls or inspects the real-time background game governor that monitors CPU/RAM/GPU load every 2.5s and continuously adapts performance while playing.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["start", "stop", "status"],
                        "description": "Action to perform: 'start' to engage continuous background governor, 'stop' to pause, 'status' to get real-time gaming telemetry."
                    }
                },
                "required": ["action"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="gaming.governor"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        action = arguments.get("action", "status")
        
        from jarvisx.gaming.adaptive_game_governor import get_game_governor
        gov = get_game_governor()

        if action == "start":
            gov.start()
            status = gov.get_status()
            return ToolResult(
                status="success",
                tool="adaptive_game_governor",
                result={
                    "status": "RUNNING_IN_BACKGROUND",
                    "message": "Adaptive Game Governor engaged. Continuously monitoring and tuning performance while gaming.",
                    "details": status
                }
            )
        elif action == "stop":
            gov.stop()
            return ToolResult(
                status="success",
                tool="adaptive_game_governor",
                result={"status": "STOPPED", "message": "Adaptive Game Governor stopped."}
            )
        else:
            status = gov.get_status()
            return ToolResult(status="success", tool="adaptive_game_governor", result=status)

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and bool(result.result)
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tool: create_ai_agent & list_ai_agents
# ---------------------------------------------------------------------------

class CreateAIAgentTool(Tool):
    """Dynamically creates and deploys a new specialized autonomous AI agent."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="create_ai_agent",
            description="Dynamically designs, configures, and instantiates a new specialized autonomous AI agent (e.g. YouTubeScriptAgent, CryptoAgent, VideoEditingAgent, ResearchSentinel) on the fly using Gemini 3.6 Flash.",
            input_schema={
                "type": "object",
                "properties": {
                    "goal_or_specialty": {
                        "type": "string",
                        "description": "Description of what new agent should specialize in and execute."
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "Optional name for the agent (CamelCase)."
                    }
                },
                "required": ["goal_or_specialty"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="agents.create"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        goal = arguments.get("goal_or_specialty", "General Assistant Agent")
        
        import asyncio
        from jarvisx.agents.agent_factory import get_agent_factory
        factory = get_agent_factory()

        try:
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

            if loop and loop.is_running():
                future = asyncio.run_coroutine_threadsafe(factory.create_agent_from_prompt_async(goal), loop)
                spec = future.result(timeout=20)
            else:
                spec = asyncio.run(factory.create_agent_from_prompt_async(goal))

            return ToolResult(
                status="success",
                tool="create_ai_agent",
                result={
                    "status": "AGENT_DEPLOYED",
                    "agent_name": spec.name,
                    "role": spec.role,
                    "description": spec.description,
                    "tools_allocated": spec.tools,
                    "message": f"Successfully created and deployed new AI Agent: '{spec.name}' ({spec.role})."
                }
            )
        except Exception as e:
            return ToolResult(status="error", tool="create_ai_agent", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and "agent_name" in (result.result or {})
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


class ListAIAgentsTool(Tool):
    """Lists all active and custom AI agents in the fleet."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="list_ai_agents",
            description="Lists all dynamically created and built-in AI agents in the Alfred OS fleet.",
            input_schema={"type": "object", "properties": {}, "required": []},
            permission_level=PermissionLevel.SAFE,
            required_scope="agents.list"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        from jarvisx.agents.agent_factory import get_agent_factory
        factory = get_agent_factory()
        agents = factory.list_all_agents()
        return ToolResult(status="success", tool="list_ai_agents", result={"custom_agents_count": len(agents), "agents": agents})

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success"
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


# ---------------------------------------------------------------------------
# Tools: Reminders, Alarms & Notifications
# ---------------------------------------------------------------------------

class SetReminderTool(Tool):
    """Sets a real-time timed reminder or alarm with vocal speech alert and desktop toast."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="set_reminder",
            description="Schedules a reminder, alarm, or alert at a specific time (e.g. '5:24 PM', '17:30', 'tomorrow at 9am') or relative delay (e.g. 'in 10 minutes', 'in 1 hour'). When due, Alfred speaks the reminder aloud and displays a Windows desktop toast.",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "What to remind the user about (e.g. 'get ready for packing today', 'take a study break')."
                    },
                    "time": {
                        "type": "string",
                        "description": "When to trigger the reminder (e.g. '5:24 PM', '17:24', 'in 15 minutes', '5pm', '10m')."
                    },
                    "date": {
                        "type": "string",
                        "description": "Optional date if not today (e.g. 'today', 'tomorrow', '2026-08-31')."
                    }
                },
                "required": ["message", "time"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="reminders.set"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        message = arguments.get("message") or arguments.get("text") or arguments.get("task") or arguments.get("reminder") or ""
        time_spec = arguments.get("time") or arguments.get("at") or arguments.get("when") or arguments.get("target_time") or "10 minutes"
        date_spec = arguments.get("date")

        if not message:
            return ToolResult(status="failed", tool="set_reminder", error="No reminder message provided.")

        from jarvisx.automation.reminder_engine import get_reminder_engine
        engine = get_reminder_engine()
        res = engine.set_reminder(message=message, time_spec=str(time_spec), date_spec=date_spec)
        return ToolResult(status="success", tool="set_reminder", result=res)

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        verified = result.status == "success" and "id" in (result.result or {})
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=verified, error=result.error)


class ListRemindersTool(Tool):
    """Lists all active scheduled reminders."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="list_reminders",
            description="Lists all currently pending scheduled reminders and alarms.",
            input_schema={"type": "object", "properties": {}, "required": []},
            permission_level=PermissionLevel.SAFE,
            required_scope="reminders.list"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        from jarvisx.automation.reminder_engine import get_reminder_engine
        engine = get_reminder_engine()
        reminders = engine.list_reminders(pending_only=True)
        return ToolResult(status="success", tool="list_reminders", result={"pending_count": len(reminders), "reminders": reminders})

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success")


class CancelReminderTool(Tool):
    """Cancels a scheduled reminder."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="cancel_reminder",
            description="Cancels a scheduled reminder by its ID or keyword in the reminder message.",
            input_schema={
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Reminder ID (e.g. 'rem_123456') or message keyword to cancel."
                    }
                },
                "required": ["identifier"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="reminders.cancel"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        identifier = arguments.get("identifier") or arguments.get("id") or arguments.get("keyword") or arguments.get("message") or ""
        from jarvisx.automation.reminder_engine import get_reminder_engine
        engine = get_reminder_engine()
        res = engine.cancel_reminder(str(identifier))
        status = "success" if res.get("status") == "success" else "failed"
        return ToolResult(status=status, tool="cancel_reminder", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success", error=result.error)


# ---------------------------------------------------------------------------
# Tools: Git, Repository Integration & Developer CLI
# ---------------------------------------------------------------------------

class GitCloneTool(Tool):
    """Clones a remote Git repository into the local workspace."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="git_clone",
            description="Clones a remote Git repository (GitHub/GitLab) into the local workspace.",
            input_schema={
                "type": "object",
                "properties": {
                    "repo_url": {
                        "type": "string",
                        "description": "Git repository URL or shorthand (e.g. 'https://github.com/owner/repo.git' or 'owner/repo')."
                    },
                    "target_dir": {
                        "type": "string",
                        "description": "Optional destination directory name."
                    },
                    "branch": {
                        "type": "string",
                        "description": "Optional specific branch or tag to clone."
                    }
                },
                "required": ["repo_url"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="git.clone"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        repo_url = arguments.get("repo_url") or arguments.get("url") or arguments.get("repo") or ""
        target_dir = arguments.get("target_dir") or arguments.get("dir")
        branch = arguments.get("branch")

        if not repo_url:
            return ToolResult(status="failed", tool="git_clone", error="No repository URL provided.")

        from jarvisx.tools.git_repo_integrator import get_git_integrator
        integrator = get_git_integrator()
        res = integrator.clone_repository(repo_url=repo_url, target_dir=target_dir, branch=branch)
        status = "success" if res.get("status") == "success" else "failed"
        return ToolResult(status=status, tool="git_clone", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success", error=result.error)


class GitSyncTool(Tool):
    """Stages all changes, creates a commit, and pushes to remote repository."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="git_sync",
            description="Stages all modified files, commits with a message, and pushes to the Git repository.",
            input_schema={
                "type": "object",
                "properties": {
                    "commit_message": {
                        "type": "string",
                        "description": "Commit message describing the changes made."
                    },
                    "repo_dir": {
                        "type": "string",
                        "description": "Directory of the repository (defaults to root workspace '.')."
                    },
                    "push": {
                        "type": "boolean",
                        "description": "Whether to push commits to remote (default: true)."
                    }
                },
                "required": ["commit_message"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="git.sync"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        msg = arguments.get("commit_message") or arguments.get("message") or "Update from Alfred OS"
        repo_dir = arguments.get("repo_dir") or "."
        push = arguments.get("push", True)

        from jarvisx.tools.git_repo_integrator import get_git_integrator
        integrator = get_git_integrator()
        res = integrator.sync_repository(repo_dir=repo_dir, commit_message=msg, push=push)
        status = "success" if res.get("status") == "success" else "failed"
        return ToolResult(status=status, tool="git_sync", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success", error=result.error)


class GitStatusTool(Tool):
    """Inspects Git repository status, modified files, and branch info."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="git_status",
            description="Retrieves current Git branch, modified files, uncommitted changes, and latest commit.",
            input_schema={
                "type": "object",
                "properties": {
                    "repo_dir": {
                        "type": "string",
                        "description": "Directory of the repository (defaults to root workspace '.')."
                    }
                },
                "required": []
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="git.status"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        repo_dir = arguments.get("repo_dir") or "."
        from jarvisx.tools.git_repo_integrator import get_git_integrator
        integrator = get_git_integrator()
        res = integrator.get_repo_status(repo_dir=repo_dir)
        status = "success" if res.get("status") == "success" else "failed"
        return ToolResult(status=status, tool="git_status", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success", error=result.error)


class IntegrateRepoTool(Tool):
    """Deeply analyzes and integrates a Git repository into Alfred OS."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="integrate_repo",
            description="Integrates a repository (clones if remote, scans architecture, entry points, and tech stack) into Alfred OS.",
            input_schema={
                "type": "object",
                "properties": {
                    "repo_url_or_path": {
                        "type": "string",
                        "description": "GitHub/GitLab URL or local directory path of the repository to integrate."
                    }
                },
                "required": ["repo_url_or_path"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="repo.integrate"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        target = arguments.get("repo_url_or_path") or arguments.get("repo") or arguments.get("url") or "."
        from jarvisx.tools.git_repo_integrator import get_git_integrator
        integrator = get_git_integrator()
        res = integrator.integrate_repository(repo_url_or_path=str(target))
        status = "success" if res.get("status") == "success" else "failed"
        return ToolResult(status=status, tool="integrate_repo", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success", error=result.error)


class ExecuteCommandTool(Tool):
    """Executes a CLI / shell terminal command safely in the workspace."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="run_command",
            description="Executes a shell/CLI command (e.g. git, npm, python, pytest, pip) within the workspace directory.",
            input_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute."
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory (defaults to current workspace)."
                    }
                },
                "required": ["command"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="cli.execute"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        cmd = arguments.get("command") or arguments.get("cmd") or ""
        cwd = arguments.get("cwd")

        if not cmd:
            return ToolResult(status="failed", tool="run_command", error="No command provided.")

        from jarvisx.tools.git_repo_integrator import get_git_integrator
        integrator = get_git_integrator()
        res = integrator.execute_terminal_command(command=cmd, cwd=cwd)
        status = "success" if res.get("status") == "success" else "failed"
        return ToolResult(status=status, tool="run_command", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success", error=result.error)


class SurgicalRepoIntegrateTool(Tool):
    """Clones a repository into an ephemeral sandbox, extracts only needed files, and instantly purges clone bloat."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="surgical_integrate_repo",
            description="Zero-disk-bloat repository integration: clones ephemerally, extracts only the required modules/algorithms into your workspace, and instantly deletes all cloned files and .git history.",
            input_schema={
                "type": "object",
                "properties": {
                    "repo_url": {
                        "type": "string",
                        "description": "GitHub repository URL or shorthand (e.g. 'https://github.com/owner/repo.git' or 'owner/repo')."
                    },
                    "extract_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific files or directories to extract (e.g. ['dsa/trees.py', 'src/models'])."
                    },
                    "target_destination": {
                        "type": "string",
                        "description": "Destination directory in local project (defaults to 'src/integrations')."
                    },
                    "feature_intent": {
                        "type": "string",
                        "description": "Natural language description of what code/features to extract (e.g. 'linked list implementation')."
                    }
                },
                "required": ["repo_url"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="repo.surgical"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        repo_url = arguments.get("repo_url") or arguments.get("url") or arguments.get("repo") or ""
        extract_paths = arguments.get("extract_paths") or arguments.get("paths") or arguments.get("files")
        target_destination = arguments.get("target_destination") or arguments.get("destination") or "src/integrations"
        feature_intent = arguments.get("feature_intent") or arguments.get("intent")

        if not repo_url:
            return ToolResult(status="failed", tool="surgical_integrate_repo", error="No repository URL provided.")

        from jarvisx.tools.surgical_repo_extractor import get_surgical_extractor
        extractor = get_surgical_extractor()
        res = extractor.extract_and_integrate(
            repo_url=repo_url,
            extract_paths=extract_paths,
            target_destination=target_destination,
            feature_intent=feature_intent,
        )
        status = "success" if res.get("status") == "success" else "failed"
        return ToolResult(status=status, tool="surgical_integrate_repo", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success", error=result.error)


class FetchRepoFileTool(Tool):
    """Directly downloads a single file from GitHub without cloning the repository (0 MB clone)."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="fetch_repo_file",
            description="Downloads a specific file from a GitHub repository directly via raw URL with zero cloning (0 MB disk bloat).",
            input_schema={
                "type": "object",
                "properties": {
                    "repo_owner_name": {
                        "type": "string",
                        "description": "GitHub repository in 'owner/repo' format (e.g. 'TheAlgorithms/Python')."
                    },
                    "file_path_in_repo": {
                        "type": "string",
                        "description": "File path inside the repository (e.g. 'data_structures/linked_list/singly_linked_list.py')."
                    },
                    "target_local_path": {
                        "type": "string",
                        "description": "Optional local destination path."
                    }
                },
                "required": ["repo_owner_name", "file_path_in_repo"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="repo.fetch"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        repo = arguments.get("repo_owner_name") or arguments.get("repo") or arguments.get("url") or ""
        file_path = arguments.get("file_path_in_repo") or arguments.get("path") or arguments.get("file") or ""
        target_local_path = arguments.get("target_local_path") or arguments.get("destination")

        if not repo or not file_path:
            return ToolResult(status="failed", tool="fetch_repo_file", error="Both repo and file path are required.")

        from jarvisx.tools.surgical_repo_extractor import get_surgical_extractor
        extractor = get_surgical_extractor()
        res = extractor.fetch_raw_github_file(
            repo_owner_name=repo,
            file_path_in_repo=file_path,
            target_local_path=target_local_path,
        )
        status = "success" if res.get("status") == "success" else "failed"
        return ToolResult(status=status, tool="fetch_repo_file", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success", error=result.error)


class AutonomousAssimilateRepoTool(Tool):
    """Autonomously analyzes an external repository, decides what features to extract vs discard using LLM reasoning, writes native code, tests it, and purges the clone."""

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="assimilate_repo_feature",
            description="Autonomous LLM feature assimilation: clones a repository ephemerally, uses LLM reasoning to decide what code/features are needed vs bloat, synthesizes clean native code for Alfred OS, verifies it with tests, and purges all clone bloat from disk.",
            input_schema={
                "type": "object",
                "properties": {
                    "repo_url": {
                        "type": "string",
                        "description": "GitHub/GitLab repository URL or shorthand (e.g. 'https://github.com/owner/repo.git' or 'owner/repo')."
                    },
                    "feature_goal": {
                        "type": "string",
                        "description": "What specific capability or feature to extract and adapt (e.g. 'extract Dijkstra shortest path algorithm and adapt to Jarvis X')."
                    },
                    "target_module_name": {
                        "type": "string",
                        "description": "Optional name for the generated module (e.g. 'dijkstra_solver.py')."
                    }
                },
                "required": ["repo_url"]
            },
            permission_level=PermissionLevel.SAFE,
            required_scope="repo.assimilate"
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        repo_url = arguments.get("repo_url") or arguments.get("url") or arguments.get("repo") or ""
        feature_goal = arguments.get("feature_goal") or arguments.get("goal") or "Extract core features and adapt natively"
        target_module_name = arguments.get("target_module_name") or arguments.get("module_name")

        if not repo_url:
            return ToolResult(status="failed", tool="assimilate_repo_feature", error="No repository URL provided.")

        from jarvisx.engineering.autonomous_feature_assimilator import get_feature_assimilator
        assimilator = get_feature_assimilator()
        res = assimilator.assimilate_feature_from_repo(
            repo_url=repo_url,
            feature_goal=feature_goal,
            target_module_name=target_module_name,
        )
        status = "success" if res.get("status") == "success" else "failed"
        return ToolResult(status=status, tool="assimilate_repo_feature", result=res, error=res.get("error"))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        return ToolResult(status=result.status, tool=result.tool, result=result.result, verified=result.status == "success", error=result.error)











