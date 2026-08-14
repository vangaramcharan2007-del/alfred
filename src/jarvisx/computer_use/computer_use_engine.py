"""High-Level Computer Use Engine for Jarvis X: GENESIS.

Separates WHAT should happen (Agent reasoning/intent) from HOW to interact (UACC).
Orchestrates multi-step GUI actions across MS Paint, VS Code, Browser, and Desktop.
"""

from __future__ import annotations
import time
import subprocess
import shutil
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

from jarvisx.computer_use.uacc_adapter import UACCAdapter, get_uacc_adapter


class ComputerUseEngine:
    """High-level desktop automation orchestrator backed by UACC."""

    def __init__(self, uacc: Optional[UACCAdapter] = None):
        self.uacc = uacc or get_uacc_adapter()

    def launch_app(self, app_name: str) -> Dict[str, Any]:
        """Launch and bring an application to the foreground."""
        name = app_name.lower().strip()
        creation_flags = 0x08000000 if sys.platform == "win32" else 0

        try:
            if "paint" in name or "mspaint" in name:
                subprocess.Popen(["mspaint.exe"], creationflags=creation_flags)
                time.sleep(1.0)
                return {"status": "success", "app": "MS Paint", "action": "launched"}
            elif "code" in name or "vscode" in name:
                code_bin = shutil.which("code") or "code"
                subprocess.Popen([code_bin, "."], shell=True, creationflags=creation_flags)
                time.sleep(1.5)
                return {"status": "success", "app": "VS Code", "action": "launched"}
            elif "notepad" in name:
                subprocess.Popen(["notepad.exe"], creationflags=creation_flags)
                time.sleep(0.5)
                return {"status": "success", "app": "Notepad", "action": "launched"}
            elif "browser" in name or "edge" in name or "chrome" in name:
                import webbrowser
                webbrowser.open("https://www.google.com")
                return {"status": "success", "app": "Browser", "action": "launched"}
            else:
                subprocess.Popen([app_name], shell=True, creationflags=creation_flags)
                return {"status": "success", "app": app_name, "action": "launched"}
        except Exception as e:
            return {"status": "failed", "app": app_name, "error": str(e)}

    def draw_shape_in_paint(self, shape: str = "rectangle") -> Dict[str, Any]:
        """Use UACC drag capabilities to draw a geometric shape in MS Paint."""
        # 1. Launch Paint if not open
        self.launch_app("mspaint")
        time.sleep(1.0)

        # 2. Inspect screen
        screen_info = self.uacc.inspect_screen()
        w = screen_info["screen"]["width"]
        h = screen_info["screen"]["height"]

        # Center canvas coordinates
        cx = w // 2
        cy = h // 2

        # 3. Draw shape via UACC drag sequences
        start_t = time.time()
        strokes = []
        if shape == "rectangle" or shape == "box":
            strokes.append(self.uacc.drag(cx - 100, cy - 100, cx + 100, cy - 100, duration=0.2))
            strokes.append(self.uacc.drag(cx + 100, cy - 100, cx + 100, cy + 100, duration=0.2))
            strokes.append(self.uacc.drag(cx + 100, cy + 100, cx - 100, cy + 100, duration=0.2))
            strokes.append(self.uacc.drag(cx - 100, cy + 100, cx - 100, cy - 100, duration=0.2))
        elif shape == "triangle":
            strokes.append(self.uacc.drag(cx, cy - 100, cx + 100, cy + 100, duration=0.2))
            strokes.append(self.uacc.drag(cx + 100, cy + 100, cx - 100, cy + 100, duration=0.2))
            strokes.append(self.uacc.drag(cx - 100, cy + 100, cx, cy - 100, duration=0.2))
        else:
            # Circle or custom
            strokes.append(self.uacc.drag(cx - 80, cy, cx, cy - 80, duration=0.2))
            strokes.append(self.uacc.drag(cx, cy - 80, cx + 80, cy, duration=0.2))
            strokes.append(self.uacc.drag(cx + 80, cy, cx, cy + 80, duration=0.2))
            strokes.append(self.uacc.drag(cx, cy + 80, cx - 80, cy, duration=0.2))

        return {
            "status": "success",
            "app": "MS Paint",
            "shape": shape,
            "strokes_drawn": len(strokes),
            "total_latency_ms": round((time.time() - start_t) * 1000, 1)
        }

    def type_code_in_vscode(self, filename: str, code_content: str) -> Dict[str, Any]:
        """Save file to workspace, open in VS Code, and bring to focus."""
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(code_content, encoding="utf-8")

        # Open in VS Code
        creation_flags = 0x08000000 if sys.platform == "win32" else 0
        code_bin = shutil.which("code") or "code"
        try:
            subprocess.Popen([code_bin, "-r", str(file_path.resolve())], shell=True, creationflags=creation_flags)
            time.sleep(1.0)
        except Exception:
            pass

        return {
            "status": "success",
            "filename": str(file_path.name),
            "path": str(file_path.resolve()),
            "lines": len(code_content.splitlines()),
            "size_bytes": len(code_content)
        }


_GLOBAL_COMPUTER_USE_ENGINE: Optional[ComputerUseEngine] = None


def get_computer_use_engine() -> ComputerUseEngine:
    global _GLOBAL_COMPUTER_USE_ENGINE
    if _GLOBAL_COMPUTER_USE_ENGINE is None:
        _GLOBAL_COMPUTER_USE_ENGINE = ComputerUseEngine()
    return _GLOBAL_COMPUTER_USE_ENGINE
