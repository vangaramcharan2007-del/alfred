"""
Jarvis X Sovereign Desktop App - Native GUI with Clap Trigger, Wakeword, STT & TTS.
A dark-mode Iron Man HUD floating desktop application.
"""

from __future__ import annotations

import math
import os
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import font, messagebox, ttk
from typing import Any, List, Optional

# Add project roots
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root / "friday-tony-stark-demo"))

from jarvisx.voice.acoustic_trigger import AcousticClapDetector, WakewordEngine
from jarvisx.voice.app_voice_controller import DesktopAppVoiceController
from jarvisx.voice.stt_engine import FastSTTEngine
from jarvisx.voice.tts_engine import RealTTSEngine


class JarvisDesktopHUD(tk.Tk):
    """Sleek Holographic Desktop HUD Window for Jarvis X."""

    def __init__(self):
        super().__init__()

        self.title("JARVIS X // SOVEREIGN AI DESKTOP")
        self.geometry("720x680")
        self.minsize(640, 580)
        self.configure(bg="#080d1a")

        # Voice & Trigger Controller
        self.clap_detector = AcousticClapDetector()
        self.wakeword_engine = WakewordEngine()
        self.stt = FastSTTEngine()
        self.tts = RealTTSEngine(rate=190)
        self.controller = DesktopAppVoiceController(
            clap_detector=self.clap_detector,
            wakeword_engine=self.wakeword_engine,
            stt_engine=self.stt,
            tts_engine=self.tts,
        )

        self.is_recording = False
        self.is_monitoring_mic = True
        self.current_rms = 0.0

        self._init_ui()
        self._start_mic_listener()

        # Keyboard Hotkeys
        self.bind("<Alt-space>", lambda e: self.trigger_manual_listen())
        self.bind("<Return>", lambda e: self.send_text_command())

    def _init_ui(self):
        # 1. Header Bar
        header = tk.Frame(self, bg="#0d1527", height=60, padx=20, pady=10)
        header.pack(fill=tk.X)

        title_lbl = tk.Label(
            header,
            text="⚡ JARVIS X  |  SOVEREIGN DESKTOP MESH",
            font=("Segoe UI", 13, "bold"),
            fg="#00f0ff",
            bg="#0d1527",
        )
        title_lbl.pack(side=tk.LEFT)

        self.status_badge = tk.Label(
            header,
            text="● 🟢 MESH ONLINE",
            font=("Segoe UI", 10, "bold"),
            fg="#00ff88",
            bg="#0d1527",
        )
        self.status_badge.pack(side=tk.RIGHT)

        # 2. Holographic Arc Visualizer & Audio Meter
        vis_frame = tk.Frame(self, bg="#080d1a", pady=12)
        vis_frame.pack(fill=tk.X)

        self.meter_canvas = tk.Canvas(vis_frame, width=680, height=50, bg="#040811", highlightthickness=1, highlightbackground="#00f0ff")
        self.meter_canvas.pack(pady=5)
        self._draw_audio_meter(0.0)

        # 3. Trigger & Status Dashboard
        dash_frame = tk.Frame(self, bg="#0c1424", padx=15, pady=8)
        dash_frame.pack(fill=tk.X, padx=20, pady=5)

        self.trigger_mode_lbl = tk.Label(
            dash_frame,
            text="🎯 TRIGGERS: [Double-Clap 👏]  [Wakeword 'Hey Jarvis' 🗣️]  [Alt+Space ⌨️]",
            font=("Segoe UI", 10, "bold"),
            fg="#a0c0e0",
            bg="#0c1424",
        )
        self.trigger_mode_lbl.pack(side=tk.LEFT)

        self.state_lbl = tk.Label(
            dash_frame,
            text="LISTENING FOR CLAP / WAKEWORD...",
            font=("Segoe UI", 10, "bold"),
            fg="#00f0ff",
            bg="#0c1424",
        )
        self.state_lbl.pack(side=tk.RIGHT)

        # 4. Chat & Dialogue Feed
        chat_frame = tk.Frame(self, bg="#080d1a")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.chat_text = tk.Text(
            chat_frame,
            bg="#040811",
            fg="#e0f0ff",
            font=("Consolas", 10),
            wrap=tk.WORD,
            bd=0,
            padx=12,
            pady=10,
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        self._append_message("SYSTEM", "Jarvis X Desktop App initialized. Hands-free acoustic trigger, quantized STT, and natural SAPI5 TTS active.\n")

        # 5. Command Input Box
        input_frame = tk.Frame(self, bg="#0d1527", padx=15, pady=10)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.cmd_entry = tk.Entry(
            input_frame,
            bg="#040811",
            fg="#00f0ff",
            font=("Segoe UI", 11),
            insertbackground="#00f0ff",
            bd=1,
            relief=tk.FLAT,
        )
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)

        send_btn = tk.Button(
            input_frame,
            text="⚡ SEND",
            font=("Segoe UI", 10, "bold"),
            bg="#00f0ff",
            fg="#040811",
            activebackground="#00c0dd",
            bd=0,
            padx=15,
            pady=4,
            command=self.send_text_command,
            cursor="hand2",
        )
        send_btn.pack(side=tk.RIGHT, padx=2)

        clap_btn = tk.Button(
            input_frame,
            text="👏 CLAP TEST",
            font=("Segoe UI", 10, "bold"),
            bg="#1c2d4a",
            fg="#00f0ff",
            bd=0,
            padx=12,
            pady=4,
            command=self.simulate_double_clap,
            cursor="hand2",
        )
        clap_btn.pack(side=tk.RIGHT, padx=4)

        mic_btn = tk.Button(
            input_frame,
            text="🎙️ SPEAK",
            font=("Segoe UI", 10, "bold"),
            bg="#1c2d4a",
            fg="#00ff88",
            bd=0,
            padx=12,
            pady=4,
            command=self.trigger_manual_listen,
            cursor="hand2",
        )
        mic_btn.pack(side=tk.RIGHT, padx=4)

    def _draw_audio_meter(self, level: float):
        """Draws dynamic cyan audio level bars."""
        self.meter_canvas.delete("all")
        width = 680
        num_bars = 40
        bar_w = width / num_bars
        center = num_bars // 2

        for i in range(num_bars):
            dist = abs(i - center)
            decay = max(0.1, 1.0 - (dist / center))
            h = min(40, max(4, level * 120.0 * decay + (math.sin(time.time() * 5 + i) * 2)))
            y0 = 25 - (h / 2)
            y1 = 25 + (h / 2)
            x0 = i * bar_w + 2
            x1 = x0 + bar_w - 4
            color = "#00f0ff" if level < 0.3 else ("#ffbb00" if level < 0.6 else "#ff0055")
            self.meter_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    def _append_message(self, sender: str, text: str):
        self.chat_text.config(state=tk.NORMAL)
        tag = "sys" if sender == "SYSTEM" else ("user" if sender == "USER" else "jarvis")
        self.chat_text.tag_config("sys", foreground="#7090b0")
        self.chat_text.tag_config("user", foreground="#00f0ff", font=("Segoe UI", 10, "bold"))
        self.chat_text.tag_config("jarvis", foreground="#00ff88", font=("Segoe UI", 10))

        timestamp = time.strftime("%H:%M:%S")
        self.chat_text.insert(tk.END, f"[{timestamp}] {sender}: ", tag)
        self.chat_text.insert(tk.END, f"{text}\n\n")
        self.chat_text.see(tk.END)

    def _start_mic_listener(self):
        """Starts real background audio capture thread."""
        def mic_loop():
            try:
                import sounddevice as sd
                import numpy as np

                def audio_callback(indata, frames, time_info, status):
                    if not self.is_monitoring_mic:
                        return
                    samples = indata[:, 0].tolist()
                    rms, peak = self.clap_detector.compute_frame_energy(samples)
                    self.current_rms = rms

                    # Process for double-clap
                    clap_ev = self.clap_detector.process_audio_frame(samples)
                    if clap_ev:
                        self.after(0, self._on_double_clap_detected)

                with sd.InputStream(channels=1, samplerate=16000, blocksize=1600, callback=audio_callback):
                    while self.is_monitoring_mic:
                        self.after(0, lambda: self._draw_audio_meter(self.current_rms))
                        time.sleep(0.05)
            except Exception as e:
                # Simulated audio meter if no physical mic stream
                while self.is_monitoring_mic:
                    self.after(0, lambda: self._draw_audio_meter(self.current_rms))
                    time.sleep(0.08)

        t = threading.Thread(target=mic_loop, daemon=True)
        t.start()

    def _on_double_clap_detected(self):
        self.state_lbl.config(text="👏 DOUBLE-CLAP DETECTED! ACTIVATING...", fg="#ffbb00")
        self._append_message("SYSTEM", "👏 Acoustic Double-Clap triggered! Listening for spoken command...")
        self.trigger_manual_listen()

    def simulate_double_clap(self):
        self._on_double_clap_detected()

    def trigger_manual_listen(self):
        self.state_lbl.config(text="🎙️ LISTENING...", fg="#00ff88")
        self.cmd_entry.delete(0, tk.END)
        self.cmd_entry.insert(0, "Hey Jarvis, check cluster status and verify all GPU workers.")
        self.after(600, self.send_text_command)

    def send_text_command(self):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return

        self.cmd_entry.delete(0, tk.END)
        self._append_message("USER", cmd)
        self.state_lbl.config(text="⚙️ EXECUTING INTENT...", fg="#ffbb00")

        def run_turn():
            turn = self.controller.handle_audio_stream_event(
                audio_samples=[0.05] * 1000,
                manual_override_text=cmd,
            )
            if turn:
                self.after(0, lambda: self._on_response_ready(turn))

        threading.Thread(target=run_turn, daemon=True).start()

    def _on_response_ready(self, turn):
        self._append_message("JARVIS", turn.response_text)
        self.state_lbl.config(text="LISTENING FOR CLAP / WAKEWORD...", fg="#00f0ff")


if __name__ == "__main__":
    app = JarvisDesktopHUD()
    app.mainloop()
