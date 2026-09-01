"""
Minimalist Floating Logo Overlay Widget for E-V & Alfred.
=========================================================
A sleek, transparent, draggable, always-on-top pill widget featuring pure symbolic logos:
- 🕷️ (E-V Math Vision & Solver)
- 🎙️ (Handy Push-to-Talk Voice Dictation)
- ❄️ (Turbo Cool RAM Purge)
- 🦇 (Alfred Sovereign Health Doctor)

Zero text clutter, pure minimalism & instant actuation.
"""

import sys
import os
import threading
import tkinter as tk

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from jarvisx.automation.ev_master_automation_engine import EVMasterAutomationEngine
from jarvisx.voice.ev_handy_engine import EVHandyVoiceDictationEngine
from jarvisx.automation.ev_neural_voice import speak_ev_neural


class EVMinimalistLogoOverlay:
    """Floating Cyber-Minimalist Logo Overlay Button Bar."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("E-V // Alfred Logo Overlay")
        self.root.overrideredirect(True)  # Borderless floating pill
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 0.92)   # Sleek glass opacity
        self.root.configure(bg="#0b0f19")

        # Screen dimensions and positioning (top-right floating pill)
        sw = self.root.winfo_screenwidth()
        pos_x = sw - 280
        pos_y = 60
        self.root.geometry(f"250x54+{pos_x}+{pos_y}")

        # Dragging mechanics
        self._drag_x = 0
        self._drag_y = 0
        self.root.bind("<ButtonPress-1>", self._start_drag)
        self.root.bind("<B1-Motion>", self._on_drag)

        self._build_ui()

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() - self._drag_x + event.x
        y = self.root.winfo_y() - self._drag_y + event.y
        self.root.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # Outer border frame
        container = tk.Frame(self.root, bg="#161b22", bd=1, relief="solid")
        container.pack(fill="both", expand=True, padx=2, pady=2)

        inner = tk.Frame(container, bg="#0d1117")
        inner.pack(fill="both", expand=True, padx=3, pady=3)

        # Drag handle indicator
        grip = tk.Label(inner, text="⋮", font=("Segoe UI", 12, "bold"), fg="#484f58", bg="#0d1117", cursor="fleur")
        grip.pack(side="left", padx=(2, 4))
        grip.bind("<ButtonPress-1>", self._start_drag)
        grip.bind("<B1-Motion>", self._on_drag)

        # 1. 🕷️ E-V Spider Math Vision Button
        btn_spider = self._create_icon_btn(inner, "🕷️", "#ff0055", self._on_spider_click, "E-V Math Vision")
        btn_spider.pack(side="left", padx=3)

        # 2. 🎙️ Handy Voice Dictation Button
        btn_handy = self._create_icon_btn(inner, "🎙️", "#58a6ff", self._on_handy_click, "Handy Voice Dictation")
        btn_handy.pack(side="left", padx=3)

        # 3. ❄️ Turbo Cool RAM Purge Button
        btn_cool = self._create_icon_btn(inner, "❄️", "#39d353", self._on_cool_click, "Turbo Cool RAM")
        btn_cool.pack(side="left", padx=3)

        # 4. 🦇 Alfred Sovereign Butler Button
        btn_bat = self._create_icon_btn(inner, "🦇", "#d29922", self._on_bat_click, "Alfred Butler Doctor")
        btn_bat.pack(side="left", padx=3)

        # 5. ✖ Close / Minimize Button
        btn_close = tk.Button(
            inner, text="×", font=("Segoe UI", 10, "bold"), fg="#8b949e", bg="#0d1117",
            activebackground="#21262d", activeforeground="#f85149", bd=0, cursor="hand2",
            command=self.root.destroy
        )
        btn_close.pack(side="right", padx=(2, 4))

    def _create_icon_btn(self, parent, icon: str, color: str, command, tooltip: str):
        btn = tk.Button(
            parent,
            text=icon,
            font=("Segoe UI Emoji", 14),
            fg=color,
            bg="#161b22",
            activebackground="#30363d",
            activeforeground="#ffffff",
            bd=0,
            padx=4,
            pady=0,
            cursor="hand2",
            command=command
        )
        return btn

    def _on_spider_click(self):
        print("\n[LOGO OVERLAY] 🕷️ E-V Math Vision Triggered!")
        threading.Thread(
            target=lambda: EVMasterAutomationEngine.get_instance().level_2_screen_vision_solve(),
            daemon=True
        ).start()

    def _on_handy_click(self):
        print("\n[LOGO OVERLAY] 🎙️ Handy Voice Dictation Triggered!")
        threading.Thread(
            target=lambda: EVHandyVoiceDictationEngine.get_instance().execute_push_to_talk_cycle(duration_sec=3.5),
            daemon=True
        ).start()

    def _on_cool_click(self):
        print("\n[LOGO OVERLAY] ❄️ Turbo Cool RAM Purge Triggered!")
        threading.Thread(
            target=lambda: EVMasterAutomationEngine.get_instance().level_5_turbo_cool(),
            daemon=True
        ).start()

    def _on_bat_click(self):
        print("\n[LOGO OVERLAY] 🦇 Alfred Sovereign Doctor Triggered!")
        threading.Thread(
            target=lambda: EVMasterAutomationEngine.get_instance().level_1_hotkey_action("F8"),
            daemon=True
        ).start()

    def run(self):
        self.root.mainloop()


def launch_overlay():
    app = EVMinimalistLogoOverlay()
    app.run()


if __name__ == "__main__":
    launch_overlay()
