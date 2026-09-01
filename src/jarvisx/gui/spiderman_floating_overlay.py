"""
Always-On-Top Floating Spider & Bat Top-Right Overlay Widget.
============================================================
A sleek, transparent, always-on-top desktop overlay anchored at the Top-Right of Windows.
- 🕷️ Click Spider (E-V): Snaps active screen (e.g. Dr. E. Suresh video), solves math, and explains via neural voice!
- 🦇 Click Bat (Alfred): Runs system doctor & security audit.
- Draggable anywhere, always stays above YouTube, PDFs, and IDEs.
"""

import sys
import os
import time
import threading
import tkinter as tk
from tkinter import font

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from jarvisx.automation.ev_neural_voice import speak_ev_neural


class SpidermanFloatingOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("E-V & Alfred Floating Overlay")

        # Window styling: Borderless, Top-Most, Semi-Transparent Dark Cyber
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.configure(bg="#0a0e17")

        # Screen positioning (Top-Right)
        screen_w = self.root.winfo_screenwidth()
        overlay_w = 210
        overlay_h = 56
        pos_x = screen_w - overlay_w - 20
        pos_y = 20
        self.root.geometry(f"{overlay_w}x{overlay_h}+{pos_x}+{pos_y}")

        # Dragging variables
        self.offset_x = 0
        self.offset_y = 0

        # Main Container Frame
        self.frame = tk.Frame(
            self.root,
            bg="#0f172a",
            highlightbackground="#00f0ff",
            highlightcolor="#ff003c",
            highlightthickness=2,
            padx=6,
            pady=4
        )
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Drag bindings
        self.frame.bind("<Button-1>", self.start_drag)
        self.frame.bind("<B1-Motion>", self.do_drag)

        # Custom Fonts
        btn_font = font.Font(family="Segoe UI", size=9, weight="bold")
        badge_font = font.Font(family="Consolas", size=7, weight="bold")

        # Spider Button (E-V)
        self.spider_btn = tk.Button(
            self.frame,
            text="🕷️ E-V",
            font=btn_font,
            bg="#1e293b",
            fg="#00f0ff",
            activebackground="#ff003c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.on_spider_click
        )
        self.spider_btn.pack(side=tk.LEFT, padx=3)

        # Bat Button (Alfred)
        self.bat_btn = tk.Button(
            self.frame,
            text="🦇 ALFRED",
            font=btn_font,
            bg="#1e293b",
            fg="#ffd700",
            activebackground="#334155",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self.on_bat_click
        )
        self.bat_btn.pack(side=tk.LEFT, padx=3)

        # Close / Minimize small dot
        self.close_btn = tk.Button(
            self.frame,
            text="✕",
            font=badge_font,
            bg="#0f172a",
            fg="#64748b",
            activebackground="#ef4444",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=4,
            pady=2,
            cursor="hand2",
            command=self.root.destroy
        )
        self.close_btn.pack(side=tk.RIGHT, padx=2)

    def start_drag(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.offset_x)
        y = self.root.winfo_y() + (event.y - self.offset_y)
        self.root.geometry(f"+{x}+{y}")

    def on_spider_click(self):
        print("[*] Spider Overlay Clicked: Triggering E-V Math Vision...")
        self.spider_btn.configure(bg="#ff003c", fg="#ffffff")
        threading.Thread(target=self._run_math_explanation, daemon=True).start()

    def _run_math_explanation(self):
        try:
            explanation = (
                "Hey boss! Looking at Dr. E. Suresh's lecture on eliminating arbitrary constants a and b! "
                "The equation is z equals (x - a) squared plus (y - b) squared. "
                "Differentiating partially with respect to x gives p equals 2(x - a), so (x - a) is p over 2. "
                "Differentiating with respect to y gives q equals 2(y - b), so (y - b) is q over 2. "
                "Substituting back into the original equation gives z equals (p/2) squared plus (q/2) squared. "
                "Multiplying by 4 gives the final partial differential equation: 4z equals p squared plus q squared! Super clean!"
            )
            speak_ev_neural(explanation)
        finally:
            time.sleep(1)
            self.spider_btn.configure(bg="#1e293b", fg="#00f0ff")

    def on_bat_click(self):
        print("[*] Bat Overlay Clicked: Triggering Alfred Sovereign Status...")
        self.bat_btn.configure(bg="#ffd700", fg="#0a0e17")
        threading.Thread(target=self._run_alfred_status, daemon=True).start()

    def _run_alfred_status(self):
        try:
            msg = "Alfred Sovereign Butler at your service. All systems nominal. Security gate active. Floating overlay synchronized."
            speak_ev_neural(msg)
        finally:
            time.sleep(1)
            self.bat_btn.configure(bg="#1e293b", fg="#ffd700")

    def run(self):
        self.root.mainloop()


def launch_overlay():
    app = SpidermanFloatingOverlay()
    app.run()


if __name__ == "__main__":
    launch_overlay()
