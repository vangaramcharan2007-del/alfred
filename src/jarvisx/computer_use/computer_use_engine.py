"""High-Level Computer Use Engine for Jarvis X: GENESIS.

Separates WHAT should happen (Agent reasoning/intent) from HOW to interact (UACC).
Orchestrates multi-step GUI actions across MS Paint, VS Code, Browser, and Desktop.
"""

from __future__ import annotations
import time
import subprocess
import shutil
import sys
import asyncio
import json
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

    async def draw_artwork_via_uacc_mcp(self, character: str = "zoro") -> Dict[str, Any]:
        """Execute complex artwork drawing through the full Agent -> MCP Client -> UACC Server -> MS Paint pipeline."""
        from jarvisx.mcp.mcp_client import MCPClient
        from jarvisx.computer_use.art_synthesizer import ArtSynthesizer
        from jarvisx.observability.computer_use_logger import get_computer_use_logger

        logger = get_computer_use_logger()
        t0 = time.time()

        # 1. Launch & Connect Standalone UACC MCP Server
        server_cmd = [sys.executable, "-m", "jarvisx.mcp.uacc_server"]
        mcp_client = MCPClient(server_id="uacc_desktop_server", command=server_cmd)
        
        connected = await mcp_client.connect(timeout_sec=4.0)
        if not connected:
            return {"status": "failed", "error": "Could not connect to UACC MCP Server"}

        try:
            # 2. Launch MS Paint via MCP
            launch_res = await mcp_client.call_tool("uacc_launch_app", {"app_name": "mspaint"})
            await asyncio.sleep(1.0)

            # 3. Inspect Screen via MCP
            inspect_res = await mcp_client.call_tool("uacc_inspect_screen", {})
            screen_info = json.loads(inspect_res.get("content", [{}])[0].get("text", "{}")) if inspect_res.get("content") else {}
            w = screen_info.get("width", 1920)
            h = screen_info.get("height", 1080)

            # Calculate canvas center offset
            cx = w // 2
            cy = h // 2

            # 4. Generate Complex Vector Art Strokes
            char_clean = character.lower().strip()
            if "luffy" in char_clean or "vs" in char_clean or ("luffy" in char_clean and "zoro" in char_clean):
                strokes = ArtSynthesizer.generate_luffy_vs_zoro_strokes(cx, cy)
                art_name = "Luffy vs Zoro (Straw Hat Duel)"
            elif "iron" in char_clean or "stark" in char_clean:
                strokes = ArtSynthesizer.generate_ironman_strokes(cx, cy)
                art_name = "Iron Man MK-85"
            else:
                strokes = ArtSynthesizer.generate_zoro_strokes(cx, cy)
                art_name = "Roronoa Zoro (Three-Sword Style)"

            print(f"[UACC MCP PIPELINE] Drawing {art_name} via {len(strokes)} continuous vector strokes in MS Paint...")

            # 5. Execute Stroke Sequence over UACC MCP JSON-RPC
            draw_res = await mcp_client.call_tool("uacc_draw_stroke_sequence", {"strokes": strokes}, timeout_sec=30.0)

            total_latency = round((time.time() - t0) * 1000, 1)

            logger.log_action(
                task_id=f"uacc_art_{int(time.time()*1000)}",
                tool="uacc_draw_stroke_sequence",
                action=f"draw_{character}",
                success=draw_res.get("status") == "success",
                latency_ms=total_latency,
                params={"character": art_name, "strokes_count": len(strokes)}
            )

            return {
                "status": "success",
                "character": art_name,
                "strokes_drawn": len(strokes),
                "mcp_server": "uacc-mcp-server",
                "transport": "JSON-RPC 2.0 stdio",
                "total_latency_ms": total_latency,
                "pipeline": "Jarvis Agent -> MCP Client -> UACC MCP Server -> Windows -> MS Paint"
            }
        finally:
            await mcp_client.disconnect()

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
