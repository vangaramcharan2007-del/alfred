"""
Ultra-Minimalist Floating Dual-Symbol Overlay (Spider & Bat Logos Only).
=======================================================================
Zero text. Pure minimalist cyber-symbols:
- 🕷️ Spider Emblem (E-V Voice & Math Vision)
- 🦇 Bat Emblem (Alfred Sovereign Butler)
Always-on-top, draggable, floating at Top-Right of screen.
"""

import sys
import os
import time
import threading
import tkinter as tk
from tkinter import font

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from jarvisx.automation.ev_neural_voice import speak_ev_neural


class MinimalistCrestOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Crest Overlay")

        # Window properties
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.94)
        self.root.configure(bg="#050811")

        # Position at top-right
        screen_w = self.root.winfo_screenwidth()
        overlay_w = 118
        overlay_h = 52
        pos_x = screen_w - overlay_w - 30
        pos_y = 25
        self.root.geometry(f"{overlay_w}x{overlay_h}+{pos_x}+{pos_y}")

        # Dragging handlers
        self.offset_x = 0
        self.offset_y = 0

        # Main Capsule Frame
        self.frame = tk.Frame(
            self.root,
            bg="#0b1120",
            highlightbackground="#00f0ff",
            highlightcolor="#ffd700",
            highlightthickness=2,
            padx=4,
            pady=3
        )
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.frame.bind("<Button-1>", self.start_drag)
        self.frame.bind("<B1-Motion>", self.do_drag)

        icon_font = font.Font(family="Segoe UI Emoji", size=16, weight="bold")

        # Pure Spider Icon Button
        self.spider_btn = tk.Button(
            self.frame,
            text="🕷️",
            font=icon_font,
            bg="#111c35",
            fg="#00f0ff",
            activebackground="#ff003c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=6,
            pady=0,
            cursor="hand2",
            command=self.on_spider_click
        )
        self.spider_btn.pack(side=tk.LEFT, padx=3, pady=2)

        # Pure Bat Icon Button
        self.bat_btn = tk.Button(
            self.frame,
            text="🦇",
            font=icon_font,
            bg="#111c35",
            fg="#ffd700",
            activebackground="#334155",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=6,
            pady=0,
            cursor="hand2",
            command=self.on_bat_click
        )
        self.bat_btn.pack(side=tk.LEFT, padx=3, pady=2)

        # Ensure top-most on start
        self.root.lift()
        self.root.focus_force()

    def start_drag(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self.offset_x)
        y = self.root.winfo_y() + (event.y - self.offset_y)
        self.root.geometry(f"+{x}+{y}")

    def on_spider_click(self):
        self.spider_btn.configure(bg="#ff003c")
        threading.Thread(target=self._speak_spider, daemon=True).start()

    def _speak_spider(self):
        try:
            msg = "E-V online! Math Vision and Voice pair programming active, boss!"
            speak_ev_neural(msg)
        finally:
            time.sleep(1)
            self.spider_btn.configure(bg="#111c35")

    def on_bat_click(self):
        self.bat_btn.configure(bg="#ffd700")
        threading.Thread(target=self._speak_bat, daemon=True).start()

    def _speak_bat(self):
        try:
            msg = "Alfred online. Sovereign systems nominal and fully protected."
            speak_ev_neural(msg)
        finally:
            time.sleep(1)
            self.bat_btn.configure(bg="#111c35")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MinimalistCrestOverlay()
    app.run()
