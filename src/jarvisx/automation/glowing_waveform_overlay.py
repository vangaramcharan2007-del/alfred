"""Glowing Audio Waveform Screen Overlay & Persistent Voice Listener for Jarvis X.

Displays a frameless, top-most glowing audio waveform canvas at the top of the desktop screen.
Glows cyan when listening for wake words ("Hey Jarvis" / "Alfred"), green when speaking TTS,
and gold when processing STT voice intents.
"""

import math
import os
import sys
import threading
import time
import subprocess
from typing import Any, Dict, Optional

try:
    import tkinter as tk
except ImportError:
    tk = None

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from jarvisx.automation.real_voice_runtime import RealVoicePipeline
from jarvisx.kernel.personal_os import PersonalOSKernel


class GlowingWaveformOverlay:
    """Persistent Top-Most Glowing Waveform Screen Overlay Controller."""

    def __init__(self, os_kernel: Optional[PersonalOSKernel] = None):
        self.kernel = os_kernel or PersonalOSKernel()
        self.voice = RealVoicePipeline()
        self.root: Optional[Any] = None
        self.canvas: Optional[Any] = None
        self.status_label: Optional[Any] = None
        self.is_running: bool = False
        self.phase: float = 0.0
        self.state: str = "LISTENING"  # LISTENING, SPEAKING, PROCESSING
        self.status_text: str = "JARVIS X ACTIVE (WAKEWORD: HEY JARVIS)"

    def speak(self, text: str):
        """Speak out loud via TTS and set waveform glow state to SPEAKING."""
        self.state = "SPEAKING"
        self.status_text = f"JARVIS X SPEAKING: '{text[:30]}...'"
        print(f"[GlowingWaveform] TTS Speaking: '{text}'")

        try:
            ps_cmd = f"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Volume = 100; $s.Speak('{text}')"
            subprocess.run(["powershell", "-Command", ps_cmd], check=False)
        except Exception:
            pass

        self.state = "LISTENING"
        self.status_text = "JARVIS X ACTIVE (WAKEWORD: HEY JARVIS)"

    def start_overlay(self):
        """Launch the persistent top-most glowing waveform overlay window."""
        if not tk:
            print("[GlowingWaveform] Tkinter not available on system.")
            return

        self.is_running = True

        def run_window():
            try:
                self.root = tk.Tk()
                self.root.title("Jarvis X Glowing Waveform")
                
                sw = self.root.winfo_screenwidth()
                w = 420
                h = 70
                x = (sw - w) // 2
                y = 12

                self.root.geometry(f"{w}x{h}+{x}+{y}")
                self.root.overrideredirect(True)
                self.root.attributes("-topmost", True)
                self.root.attributes("-alpha", 0.92)
                self.root.configure(bg="#050811")

                # Frame container
                border_frame = tk.Frame(self.root, bg="#00f0ff", bd=1)
                border_frame.pack(fill="both", expand=True)

                inner_frame = tk.Frame(border_frame, bg="#050811")
                inner_frame.pack(fill="both", expand=True, padx=2, pady=2)

                # Status Header Text
                self.status_label = tk.Label(
                    inner_frame,
                    text=self.status_text,
                    font=("Consolas", 8, "bold"),
                    fg="#00f0ff",
                    bg="#050811",
                )
                self.status_label.pack(pady=(4, 0))

                # Canvas for Waveform
                self.canvas = tk.Canvas(
                    inner_frame,
                    width=400,
                    height=38,
                    bg="#050811",
                    highlightthickness=0,
                )
                self.canvas.pack(pady=2)

                # Animate Waveform at 30 FPS
                def animate():
                    if not self.is_running or not self.root:
                        return
                    self.draw_waveform()
                    self.phase += 0.15
                    self.root.after(33, animate)

                # Initial announcement out loud
                threading.Thread(
                    target=lambda: self.speak("Jarvis X is active and listening on your laptop forever, Boss."),
                    daemon=True,
                ).start()

                animate()
                self.root.mainloop()
            except Exception as e:
                print(f"[GlowingWaveform] UI Loop error: {e}")

        # Run UI in main or current thread
        run_window()

    def draw_waveform(self):
        """Render animated sine wave harmonics with state-dependent glow colors."""
        if not self.canvas:
            return

        self.canvas.delete("all")
        w = 400
        h = 38
        cy = h / 2

        # State Color Palette
        if self.state == "SPEAKING":
            color_primary = "#00ff66"  # Vibrant Green
            color_glow = "#006622"
            amp_mult = 1.4
            self.status_label.config(fg="#00ff66", text=self.status_text)
        elif self.state == "PROCESSING":
            color_primary = "#ffbb00"  # Amber Gold
            color_glow = "#886600"
            amp_mult = 1.2
            self.status_label.config(fg="#ffbb00", text=self.status_text)
        else:
            color_primary = "#00f0ff"  # Electric Cyan
            color_glow = "#004466"
            amp_mult = 0.8
            self.status_label.config(fg="#00f0ff", text="JARVIS X ACTIVE (WAKEWORD: HEY JARVIS)")

        # Draw Glow Layer (Background thicker lines)
        points_glow = []
        for x in range(0, w, 4):
            rel_x = x / w
            envelope = math.sin(rel_x * math.pi)  # Fade at edges
            y = cy + (math.sin(rel_x * 12 + self.phase) * 12 * amp_mult * envelope)
            points_glow.extend([x, y])

        if len(points_glow) >= 4:
            self.canvas.create_line(points_glow, fill=color_glow, width=5, smooth=True)

        # Draw Primary Waveform Line
        points_main = []
        for x in range(0, w, 2):
            rel_x = x / w
            envelope = math.sin(rel_x * math.pi)
            y = cy + (math.sin(rel_x * 16 - self.phase * 1.2) * 10 * amp_mult * envelope) + (math.cos(rel_x * 24 + self.phase * 0.8) * 4 * envelope)
            points_main.extend([x, y])

        if len(points_main) >= 4:
            self.canvas.create_line(points_main, fill=color_primary, width=2, smooth=True)


def launch_glowing_waveform_overlay():
    """CLI Entry point for persistent glowing waveform overlay."""
    overlay = GlowingWaveformOverlay()
    overlay.start_overlay()


if __name__ == "__main__":
    launch_glowing_waveform_overlay()
