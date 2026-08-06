"""Native Windows Desktop Companion UI for Jarvis X (Layer 4 - Automation).

Sleek, semi-transparent, frameless floating desktop widget for real-time status telemetry,
voice status indicators, active goal priorities, and 1-click action triggers using tkinter.
"""

import sys
import os
import threading
import time
from typing import Any, Dict, Optional

try:
    import tkinter as tk
except ImportError:
    tk = None


class NativeCompanionUI:
    """Zero-fluff production native Windows desktop companion UI controller."""

    def __init__(self, os_kernel: Optional[Any] = None):
        self.os_kernel = os_kernel
        self.root: Optional[Any] = None
        self.is_running: bool = False
        self._thread: Optional[threading.Thread] = None

    def build_status_dict(self) -> Dict[str, Any]:
        """Synthesize live telemetry status for UI rendering."""
        if not self.os_kernel:
            return {
                "voice_status": "VOICE_READY",
                "hspw": 402.8,
                "top_priority": "Study Graph Algorithms",
                "active_goals": 2,
            }

        dash = self.os_kernel.get_master_dashboard()
        hspw = dash.get("total_hspw", 400.0)
        voice_status = getattr(self.os_kernel.real_voice, "pipeline_status", "VOICE_READY")
        goals = dash.get("active_goals", [])
        top_p = goals[0].get("goal", "Maintain Academic Progress") if goals else "Clean Temporary Storage"

        return {
            "voice_status": voice_status,
            "hspw": round(hspw, 2),
            "top_priority": top_p,
            "active_goals": len(goals),
        }

    def start_widget(self, headless: bool = False) -> Dict[str, Any]:
        """Launch the floating companion widget window in background thread if non-headless."""
        if self.is_running:
            return {"status": "ALREADY_RUNNING", "headless": headless}

        self.is_running = True

        if headless or not tk or not sys.platform.startswith("win"):
            return {
                "status": "HEADLESS_ACTIVE",
                "platform": sys.platform,
                "telemetry": self.build_status_dict(),
            }

        def run_gui():
            try:
                self.root = tk.Tk()
                self.root.title("Alfred OS Companion")
                self.root.geometry("320x180+1200+50")
                self.root.overrideredirect(True)
                self.root.attributes("-topmost", True)
                self.root.configure(bg="#0d1117")

                title_lbl = tk.Label(
                    self.root,
                    text="🤖 ALFRED OS COMPANION HUD",
                    font=("Segoe UI", 10, "bold"),
                    fg="#58a6ff",
                    bg="#0d1117",
                )
                title_lbl.pack(pady=5)

                stat = self.build_status_dict()
                info_text = f"Status: {stat['voice_status']}\nTime Saved: +{stat['hspw']} HSPW\nPriority: {stat['top_priority'][:28]}"
                self.info_label = tk.Label(
                    self.root,
                    text=info_text,
                    font=("Segoe UI", 9),
                    fg="#c9d1d9",
                    bg="#0d1117",
                    justify="left",
                )
                self.info_label.pack(pady=5)

                btn_frame = tk.Frame(self.root, bg="#0d1117")
                btn_frame.pack(pady=5)

                clean_btn = tk.Button(
                    btn_frame,
                    text="Clean PC",
                    font=("Segoe UI", 8, "bold"),
                    bg="#238636",
                    fg="#ffffff",
                    relief="flat",
                    command=lambda: self.os_kernel.execute_objective("clean pc") if self.os_kernel else None,
                )
                clean_btn.pack(side="left", padx=5)

                close_btn = tk.Button(
                    btn_frame,
                    text="Dismiss",
                    font=("Segoe UI", 8),
                    bg="#21262d",
                    fg="#8b949e",
                    relief="flat",
                    command=self.stop_widget,
                )
                close_btn.pack(side="left", padx=5)

                self.root.mainloop()
            except Exception:
                self.is_running = False

        self._thread = threading.Thread(target=run_gui, daemon=True)
        self._thread.start()

        return {
            "status": "RUNNING",
            "telemetry": self.build_status_dict(),
        }

    def stop_widget(self) -> Dict[str, Any]:
        """Close widget window safely."""
        self.is_running = False
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass
            self.root = None

        return {"status": "STOPPED"}
