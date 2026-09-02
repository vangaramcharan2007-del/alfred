"""Universal AI Computer Control (UACC) Adapter for Jarvis X: GENESIS.

Implements the official UACC desktop control specification over MCP with
native Windows Win32 API / PyAutoGUI fallback execution.

Capabilities:
- Screen Inspection & UI State Observation
- Pixel-Precise Mouse Movement, Clicking, and Dragging
- Keyboard Typing and Hotkey Actuation
- Cross-Application Interaction (MS Paint, VS Code, Browser, Terminal, Explorer)
"""

from __future__ import annotations
import os
import sys
import time
import ctypes
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

try:
    import pyautogui
    HAVE_PYAUTOGUI = True
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
except Exception:
    HAVE_PYAUTOGUI = False


@dataclass
class ScreenState:
    width: int
    height: int
    active_window_title: str
    active_window_rect: Optional[Tuple[int, int, int, int]] = None
    open_windows: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class UACCAdapter:
    """Universal AI Computer Control (UACC) adapter."""

    def __init__(self, mcp_client: Optional[Any] = None):
        self.mcp_client = mcp_client
        self._check_environment()

    def _check_environment(self):
        if HAVE_PYAUTOGUI:
            pyautogui.FAILSAFE = True

    def inspect_screen(self) -> Dict[str, Any]:
        """Inspect screen geometry, active window, and open desktop windows."""
        width, height = (1920, 1080)
        active_title = "Desktop"
        open_windows = []

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
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        active_title = buff.value

                # Enumerate visible top-level windows
                EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
                
                def enum_cb(h, lp):
                    if user32.IsWindowVisible(h):
                        l = user32.GetWindowTextLengthW(h)
                        if l > 0:
                            b = ctypes.create_unicode_buffer(l + 1)
                            user32.GetWindowTextW(h, b, l + 1)
                            t = b.value.strip()
                            if t and t not in ("Default IME", "MSCTFIME UI", "Program Manager"):
                                open_windows.append(t)
                    return True

                user32.EnumWindows(EnumWindowsProc(enum_cb), 0)
            except Exception:
                pass

        return {
            "status": "success",
            "screen": {
                "width": width,
                "height": height,
                "active_window": active_title,
                "open_windows": open_windows[:15],
                "timestamp": time.time()
            }
        }

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> Dict[str, Any]:
        """Execute deterministic mouse click at pixel coordinates (x, y)."""
        start_t = time.time()
        if HAVE_PYAUTOGUI:
            try:
                pyautogui.click(x=x, y=y, clicks=clicks, button=button)
                return {
                    "status": "success",
                    "action": "click",
                    "x": x,
                    "y": y,
                    "button": button,
                    "clicks": clicks,
                    "latency_ms": round((time.time() - start_t) * 1000, 1)
                }
            except Exception as e:
                return {"status": "failed", "action": "click", "error": str(e)}
        return {"status": "failed", "action": "click", "error": "PyAutoGUI not available"}

    def move(self, x: int, y: int, duration: float = 0.1) -> Dict[str, Any]:
        """Move mouse cursor smoothly to coordinates (x, y)."""
        if HAVE_PYAUTOGUI:
            try:
                pyautogui.moveTo(x=x, y=y, duration=duration)
                return {"status": "success", "action": "move", "x": x, "y": y}
            except Exception as e:
                return {"status": "failed", "action": "move", "error": str(e)}
        return {"status": "failed", "action": "move", "error": "PyAutoGUI not available"}

    def type(self, text: str, interval: float = 0.01) -> Dict[str, Any]:
        """Type characters reliably with standard keystroke interval."""
        start_t = time.time()
        if HAVE_PYAUTOGUI:
            try:
                pyautogui.write(text, interval=interval)
                return {
                    "status": "success",
                    "action": "type",
                    "chars_typed": len(text),
                    "latency_ms": round((time.time() - start_t) * 1000, 1)
                }
            except Exception as e:
                return {"status": "failed", "action": "type", "error": str(e)}
        return {"status": "failed", "action": "type", "error": "PyAutoGUI not available"}

    def press(self, key: str) -> Dict[str, Any]:
        """Press a keyboard key or hotkey combination (e.g. 'enter', 'ctrl+s')."""
        if HAVE_PYAUTOGUI:
            try:
                if "+" in key:
                    keys = [k.strip() for k in key.split("+")]
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(key)
                return {"status": "success", "action": "press", "key": key}
            except Exception as e:
                return {"status": "failed", "action": "press", "error": str(e)}
        return {"status": "failed", "action": "press", "error": "PyAutoGUI not available"}

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5, button: str = "left") -> Dict[str, Any]:
        """Perform mouse drag between two coordinates (ideal for drawing in MS Paint or selecting text)."""
        start_t = time.time()
        if HAVE_PYAUTOGUI:
            try:
                pyautogui.moveTo(start_x, start_y)
                pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
                return {
                    "status": "success",
                    "action": "drag",
                    "from": [start_x, start_y],
                    "to": [end_x, end_y],
                    "duration": duration,
                    "latency_ms": round((time.time() - start_t) * 1000, 1)
                }
            except Exception as e:
                return {"status": "failed", "action": "drag", "error": str(e)}
        return {"status": "failed", "action": "drag", "error": "PyAutoGUI not available"}

    def execute_action(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generic dispatch for any UACC action."""
        act = action_name.lower().strip()
        if act in ("inspect", "inspect_screen", "screen"):
            return self.inspect_screen()
        elif act in ("click", "mouse_click"):
            return self.click(x=int(params.get("x", 0)), y=int(params.get("y", 0)), button=params.get("button", "left"), clicks=int(params.get("clicks", 1)))
        elif act in ("move", "mouse_move"):
            return self.move(x=int(params.get("x", 0)), y=int(params.get("y", 0)), duration=float(params.get("duration", 0.1)))
        elif act in ("type", "write", "type_text"):
            return self.type(text=params.get("text", ""), interval=float(params.get("interval", 0.01)))
        elif act in ("press", "key", "press_key", "hotkey"):
            return self.press(key=params.get("key", "enter"))
        elif act in ("drag", "drag_mouse"):
            return self.drag(
                start_x=int(params.get("start_x", 0)),
                start_y=int(params.get("start_y", 0)),
                end_x=int(params.get("end_x", 0)),
                end_y=int(params.get("end_y", 0)),
                duration=float(params.get("duration", 0.5)),
                button=params.get("button", "left")
            )
        return {"status": "failed", "error": f"Unknown UACC action '{action_name}'"}


_GLOBAL_UACC_ADAPTER: Optional[UACCAdapter] = None


def get_uacc_adapter() -> UACCAdapter:
    global _GLOBAL_UACC_ADAPTER
    if _GLOBAL_UACC_ADAPTER is None:
        _GLOBAL_UACC_ADAPTER = UACCAdapter()
    return _GLOBAL_UACC_ADAPTER
