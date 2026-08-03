"""
Alfred Waveform Overlay - Always-on-top transparent voice waveform.
Sits at the bottom of the screen permanently, showing a live audio waveform.
Fully voice-automated: wake word "Alfred" triggers listening.
"""
from __future__ import annotations
import math
import random
import sys
import threading
import time
import tkinter as tk
from typing import Optional


class WaveformOverlay:
    """
    Transparent always-on-top waveform overlay window.
    Shows a live animated waveform that reacts to voice state.
    States: IDLE (subtle pulse), LISTENING (active waveform), SPEAKING (output waveform), PROCESSING (spin).
    """

    WIDTH = 500
    HEIGHT = 80
    BAR_COUNT = 40
    UPDATE_MS = 33  # ~30 FPS

    # Colors
    COLOR_BG = "#0a0a0a"
    COLOR_IDLE = "#1a3a5c"
    COLOR_LISTENING = "#00d4ff"
    COLOR_SPEAKING = "#00ff88"
    COLOR_PROCESSING = "#ff8800"
    COLOR_TEXT = "#88aacc"

    def __init__(self):
        self.state = "IDLE"  # IDLE, LISTENING, SPEAKING, PROCESSING
        self.status_text = "Alfred Standing By"
        self.running = True
        self._phase = 0.0
        self._bars = [0.0] * self.BAR_COUNT
        self._root: Optional[tk.Tk] = None
        self._canvas: Optional[tk.Canvas] = None
        self._label: Optional[tk.Label] = None

    def launch(self):
        """Launch the overlay window. Blocks on mainloop."""
        self._root = tk.Tk()
        self._root.title("Alfred")
        self._root.overrideredirect(True)  # No title bar
        self._root.attributes("-topmost", True)  # Always on top
        self._root.attributes("-alpha", 0.88)  # Slight transparency
        self._root.configure(bg=self.COLOR_BG)

        # Position at bottom center of screen
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = (screen_w - self.WIDTH) // 2
        y = screen_h - self.HEIGHT - 60  # 60px above taskbar
        self._root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

        # Canvas for waveform
        self._canvas = tk.Canvas(
            self._root, width=self.WIDTH, height=self.HEIGHT - 20,
            bg=self.COLOR_BG, highlightthickness=0
        )
        self._canvas.pack(side=tk.TOP)

        # Status label
        self._label = tk.Label(
            self._root, text=self.status_text, font=("Consolas", 9),
            fg=self.COLOR_TEXT, bg=self.COLOR_BG
        )
        self._label.pack(side=tk.BOTTOM)

        # Allow dragging
        self._canvas.bind("<Button-1>", self._start_drag)
        self._canvas.bind("<B1-Motion>", self._do_drag)
        self._label.bind("<Button-1>", self._start_drag)
        self._label.bind("<B1-Motion>", self._do_drag)

        # Right-click to close
        self._canvas.bind("<Button-3>", lambda e: self.shutdown())
        self._label.bind("<Button-3>", lambda e: self.shutdown())

        # Start animation loop
        self._animate()
        self._root.mainloop()

    def shutdown(self):
        self.running = False
        if self._root:
            self._root.destroy()

    def set_state(self, state: str, text: Optional[str] = None):
        self.state = state
        if text:
            self.status_text = text

    # ------------------------------------------------------------------
    # Drag support
    # ------------------------------------------------------------------
    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _do_drag(self, event):
        x = self._root.winfo_x() + event.x - self._drag_x
        y = self._root.winfo_y() + event.y - self._drag_y
        self._root.geometry(f"+{x}+{y}")

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------
    def _animate(self):
        if not self.running:
            return

        self._phase += 0.15
        canvas = self._canvas
        canvas.delete("all")

        h = self.HEIGHT - 20
        mid = h // 2
        bar_w = self.WIDTH / self.BAR_COUNT

        # Generate bar heights based on state
        if self.state == "IDLE":
            color = self.COLOR_IDLE
            for i in range(self.BAR_COUNT):
                target = 3 + 4 * math.sin(self._phase + i * 0.3)
                self._bars[i] += (target - self._bars[i]) * 0.15
        elif self.state == "LISTENING":
            color = self.COLOR_LISTENING
            for i in range(self.BAR_COUNT):
                target = 5 + random.uniform(5, 25) * abs(math.sin(self._phase * 2 + i * 0.5))
                self._bars[i] += (target - self._bars[i]) * 0.3
        elif self.state == "SPEAKING":
            color = self.COLOR_SPEAKING
            for i in range(self.BAR_COUNT):
                target = 8 + 18 * abs(math.sin(self._phase * 3 + i * 0.4))
                self._bars[i] += (target - self._bars[i]) * 0.25
        elif self.state == "PROCESSING":
            color = self.COLOR_PROCESSING
            for i in range(self.BAR_COUNT):
                wave = math.sin(self._phase * 4 - i * 0.6)
                target = 4 + 12 * max(0, wave)
                self._bars[i] += (target - self._bars[i]) * 0.2
        else:
            color = self.COLOR_IDLE

        # Draw bars (mirrored vertically around center)
        for i in range(self.BAR_COUNT):
            x1 = i * bar_w + 2
            x2 = x1 + bar_w - 3
            bar_h = max(2, self._bars[i])
            canvas.create_rectangle(
                x1, mid - bar_h, x2, mid + bar_h,
                fill=color, outline=""
            )

        # Draw center line
        canvas.create_line(0, mid, self.WIDTH, mid, fill="#1a2a3a", width=1)

        # Update label
        if self._label:
            self._label.config(text=self.status_text)

        self._root.after(self.UPDATE_MS, self._animate)


def run_overlay():
    """Entry point: launch the waveform overlay with simulated state cycling."""
    overlay = WaveformOverlay()

    def demo_cycle():
        """Cycle through states for demonstration."""
        time.sleep(2)
        states = [
            ("LISTENING", "Listening..."),
            ("PROCESSING", "Processing..."),
            ("SPEAKING", "Alfred: Running tests now."),
            ("IDLE", "Alfred Standing By"),
        ]
        while overlay.running:
            for state, text in states:
                if not overlay.running:
                    return
                overlay.set_state(state, text)
                time.sleep(3)

    t = threading.Thread(target=demo_cycle, daemon=True)
    t.start()
    overlay.launch()


if __name__ == "__main__":
    run_overlay()
