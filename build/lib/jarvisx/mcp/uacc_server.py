"""Universal AI Computer Control (UACC) Standalone MCP Server for Jarvis X.

Implements the official Model Context Protocol (MCP) specification over stdio JSON-RPC 2.0,
providing deterministic pixel-level desktop inspection and actuation.

Run directly as a subprocess:
    python -m jarvisx.mcp.uacc_server
"""

from __future__ import annotations
import sys
import json
import time
import ctypes
import subprocess
from typing import Dict, Any, List, Optional

try:
    import pyautogui
    HAVE_PYAUTOGUI = True
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.02
except Exception:
    HAVE_PYAUTOGUI = False


TOOLS_SPEC = [
    {
        "name": "uacc_inspect_screen",
        "description": "Inspect screen resolution, active foreground window, and open desktop windows.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "uacc_launch_app",
        "description": "Launch a desktop application by name (e.g. 'mspaint', 'notepad', 'code').",
        "inputSchema": {
            "type": "object",
            "properties": {"app_name": {"type": "string", "description": "Application executable or name."}},
            "required": ["app_name"]
        }
    },
    {
        "name": "uacc_mouse_click",
        "description": "Click at specific pixel coordinates (x, y).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "button": {"type": "string", "enum": ["left", "right", "middle"], "default": "left"}
            },
            "required": ["x", "y"]
        }
    },
    {
        "name": "uacc_mouse_drag",
        "description": "Drag the mouse from (start_x, start_y) to (end_x, end_y) to draw or select.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_x": {"type": "integer"},
                "start_y": {"type": "integer"},
                "end_x": {"type": "integer"},
                "end_y": {"type": "integer"},
                "duration": {"type": "number", "default": 0.15}
            },
            "required": ["start_x", "start_y", "end_x", "end_y"]
        }
    },
    {
        "name": "uacc_draw_stroke_sequence",
        "description": "Execute a sequence of connected continuous line strokes to draw complex art in MS Paint.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "strokes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "array", "items": {"type": "integer"}},
                            "end": {"type": "array", "items": {"type": "integer"}},
                            "duration": {"type": "number", "default": 0.05}
                        },
                        "required": ["start", "end"]
                    }
                }
            },
            "required": ["strokes"]
        }
    }
]


def handle_inspect_screen() -> Dict[str, Any]:
    width, height = 1920, 1080
    active_title = "Desktop"
    if HAVE_PYAUTOGUI:
        try:
            sz = pyautogui.size()
            width, height = sz.width, sz.height
        except Exception:
            pass

    if sys.platform == "win32":
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if hwnd:
                l = user32.GetWindowTextLengthW(hwnd)
                if l > 0:
                    b = ctypes.create_unicode_buffer(l + 1)
                    user32.GetWindowTextW(hwnd, b, l + 1)
                    active_title = b.value
        except Exception:
            pass

    return {
        "width": width,
        "height": height,
        "active_window": active_title,
        "timestamp": time.time()
    }


def handle_launch_app(app_name: str) -> Dict[str, Any]:
    creation_flags = 0x08000000 if sys.platform == "win32" else 0
    name = app_name.lower().strip()
    try:
        if "paint" in name or "mspaint" in name:
            subprocess.Popen(["mspaint.exe"], creationflags=creation_flags)
            time.sleep(1.0)
            return {"status": "success", "app": "MS Paint", "launched": True}
        elif "notepad" in name:
            subprocess.Popen(["notepad.exe"], creationflags=creation_flags)
            time.sleep(0.5)
            return {"status": "success", "app": "Notepad", "launched": True}
        else:
            subprocess.Popen([app_name], shell=True, creationflags=creation_flags)
            return {"status": "success", "app": app_name, "launched": True}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


def handle_mouse_drag(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.15) -> Dict[str, Any]:
    if HAVE_PYAUTOGUI:
        try:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, duration=duration, button="left")
            return {"status": "success", "from": [start_x, start_y], "to": [end_x, end_y]}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    return {"status": "failed", "error": "PyAutoGUI not available"}


def handle_stroke_sequence(strokes: List[Dict[str, Any]]) -> Dict[str, Any]:
    executed = 0
    start_t = time.time()
    if HAVE_PYAUTOGUI:
        try:
            for s in strokes:
                start = s.get("start", [0, 0])
                end = s.get("end", [0, 0])
                dur = float(s.get("duration", 0.05))
                pyautogui.moveTo(start[0], start[1])
                pyautogui.dragTo(end[0], end[1], duration=dur, button="left")
                executed += 1
            return {
                "status": "success",
                "strokes_count": executed,
                "total_time_ms": round((time.time() - start_t) * 1000, 1)
            }
        except Exception as e:
            return {"status": "failed", "strokes_count": executed, "error": str(e)}
    return {"status": "failed", "error": "PyAutoGUI not available"}


def main():
    """Stdio JSON-RPC 2.0 loop for UACC MCP Server."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "uacc-mcp-server", "version": "1.0.0"}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOLS_SPEC}
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "uacc_inspect_screen":
                    out = handle_inspect_screen()
                elif tool_name == "uacc_launch_app":
                    out = handle_launch_app(args.get("app_name", "mspaint"))
                elif tool_name == "uacc_mouse_click":
                    if HAVE_PYAUTOGUI:
                        pyautogui.click(args.get("x", 0), args.get("y", 0), button=args.get("button", "left"))
                        out = {"status": "success", "x": args.get("x"), "y": args.get("y")}
                    else:
                        out = {"status": "failed", "error": "PyAutoGUI not available"}
                elif tool_name == "uacc_mouse_drag":
                    out = handle_mouse_drag(
                        args.get("start_x", 0),
                        args.get("start_y", 0),
                        args.get("end_x", 0),
                        args.get("end_y", 0),
                        args.get("duration", 0.15)
                    )
                elif tool_name == "uacc_draw_stroke_sequence":
                    out = handle_stroke_sequence(args.get("strokes", []))
                else:
                    out = {"status": "failed", "error": f"Unknown tool '{tool_name}'"}

                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(out)}]}
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {e}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
