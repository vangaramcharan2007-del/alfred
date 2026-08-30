"""
Alfred Live Situation Room & Master Mission Control HUD.
Renders an on-screen cybernetic dashboard visualizing all 20 agents, real-time hardware telemetry,
continuous game governor sentinel status, and dynamic voice/chat mission execution.
"""

import json
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import psutil

# Ensure UTF-8 console output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to sys.path
sys.path.insert(0, os.path.abspath("src"))

from jarvisx.runtime.ambient_sovereign_orchestrator import get_ambient_orchestrator


class AlfredSituationRoomHUD:
    """Master on-screen graphical Situation Room for Alfred Sovereign Orchestrator."""

    def __init__(self):
        self.orchestrator = get_ambient_orchestrator()
        self.orchestrator.start_ambient_engine()

        self.root = tk.Tk()
        self.root.title("ALFRED OS — SOVEREIGN ORCHESTRATION SITUATION ROOM")
        self.root.geometry("920x680+200+80")
        self.root.configure(bg="#080c14")

        self._build_ui()
        self._start_update_loop()

    def _build_ui(self):
        # 1. Top Cybernetic Header
        header = tk.Frame(self.root, bg="#101726", padx=20, pady=12)
        header.pack(fill="x")

        tk.Label(
            header,
            text="⚡ ALFRED SOVEREIGN ORCHESTRATION SENTINEL",
            font=("Segoe UI", 16, "bold"),
            fg="#00d2ff",
            bg="#101726"
        ).pack(side="left")

        self.status_badge = tk.Label(
            header,
            text="● AMBIENT MODE ACTIVE",
            font=("Consolas", 10, "bold"),
            fg="#00ff88",
            bg="#16233b",
            padx=10,
            pady=4,
            relief="groove"
        )
        self.status_badge.pack(side="right")

        # 2. Main Content Split (Left Telemetry + Right Workforce)
        body = tk.Frame(self.root, bg="#080c14", padx=15, pady=10)
        body.pack(fill="both", expand=True)

        # Left Column: Telemetry & Governor
        left_col = tk.Frame(body, bg="#0d1320", padx=15, pady=12, relief="ridge", bd=1)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(
            left_col,
            text="📊 SYSTEM HARDWARE & THERMAL METERS",
            font=("Segoe UI", 11, "bold"),
            fg="#70a1ff",
            bg="#0d1320"
        ).pack(anchor="w", pady=(0, 10))

        self.cpu_var = tk.StringVar(value="CPU Load: 0%")
        tk.Label(left_col, textvariable=self.cpu_var, font=("Consolas", 10, "bold"), fg="#e0e0e0", bg="#0d1320").pack(anchor="w")
        self.cpu_bar = ttk.Progressbar(left_col, orient="horizontal", mode="determinate")
        self.cpu_bar.pack(fill="x", pady=(2, 10))

        self.ram_var = tk.StringVar(value="RAM Utilization: 0%")
        tk.Label(left_col, textvariable=self.ram_var, font=("Consolas", 10, "bold"), fg="#e0e0e0", bg="#0d1320").pack(anchor="w")
        self.ram_bar = ttk.Progressbar(left_col, orient="horizontal", mode="determinate")
        self.ram_bar.pack(fill="x", pady=(2, 10))

        self.power_var = tk.StringVar(value="Power State: AC Plugged In")
        tk.Label(left_col, textvariable=self.power_var, font=("Consolas", 10), fg="#00ff88", bg="#0d1320").pack(anchor="w", pady=(0, 10))

        tk.Label(
            left_col,
            text="🎮 ADAPTIVE GAME SENTINEL",
            font=("Segoe UI", 11, "bold"),
            fg="#e58e26",
            bg="#0d1320"
        ).pack(anchor="w", pady=(10, 5))

        self.game_var = tk.StringVar(value="Active Game: None (Monitoring every 2.5s)")
        tk.Label(left_col, textvariable=self.game_var, font=("Consolas", 10), fg="#fbc531", bg="#0d1320").pack(anchor="w")

        self.mode_var = tk.StringVar(value="Governor Policy: STANDBY_HIGH_PERFORMANCE")
        tk.Label(left_col, textvariable=self.mode_var, font=("Consolas", 10), fg="#4cd137", bg="#0d1320").pack(anchor="w")

        # Right Column: Unified Agent Workforce Matrix (22+ Agents)
        right_col = tk.Frame(body, bg="#0d1320", padx=15, pady=12, relief="ridge", bd=1)
        right_col.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(
            right_col,
            text="🤖 UNIFIED ACTIVE AGENT FLEET (22+ WORKERS)",
            font=("Segoe UI", 11, "bold"),
            fg="#a29bfe",
            bg="#0d1320"
        ).pack(anchor="w", pady=(0, 6))

        # Scrollable container for agents
        canvas = tk.Canvas(right_col, bg="#0d1320", highlightthickness=0, height=210)
        scrollbar = ttk.Scrollbar(right_col, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0d1320")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        from jarvisx.orchestration.unified_agent_fleet import get_unified_fleet
        fleet = get_unified_fleet()
        all_agents = fleet.list_agents()

        for a in all_agents:
            name = a["name"]
            st = a["status"]
            col = "#00ff88" if "Governor" in name or "Autopilot" in name or "Coding" in name else "#00d2ff"
            r = tk.Frame(scrollable_frame, bg="#121a2b", padx=8, pady=3)
            r.pack(fill="x", pady=2)
            tk.Label(r, text=f"• {name}:", font=("Segoe UI", 9, "bold"), fg="#e0e0e0", bg="#121a2b", width=24, anchor="w").pack(side="left")
            tk.Label(r, text=st, font=("Consolas", 8, "bold"), fg=col, bg="#121a2b").pack(side="left")


        # 3. Bottom Activity Log & Interactive Command Input
        bottom_f = tk.Frame(self.root, bg="#101726", padx=15, pady=10)
        bottom_f.pack(fill="both", expand=True)

        tk.Label(bottom_f, text="📜 LIVE ORCHESTRATION ACTIVITY FEED:", font=("Segoe UI", 10, "bold"), fg="#70a1ff", bg="#101726").pack(anchor="w")

        self.log_text = tk.Text(bottom_f, height=6, bg="#080c14", fg="#00ff88", font=("Consolas", 9), relief="flat", padx=8, pady=6)
        self.log_text.pack(fill="both", expand=True, pady=(3, 8))
        self.log_text.insert("end", "[ALFRED OS] Sovereign Orchestration Kernel Online.\n[ALFRED OS] Groq LPU Brain Connected (Qwen 3.8 27B — Sub-second Reflex).\n")

        # Command Dispatch Bar
        cmd_frame = tk.Frame(bottom_f, bg="#101726")
        cmd_frame.pack(fill="x")

        tk.Label(cmd_frame, text="⚡ Execute Mission:", font=("Segoe UI", 10, "bold"), fg="#e0e0e0", bg="#101726").pack(side="left", padx=(0, 6))

        self.cmd_entry = tk.Entry(cmd_frame, font=("Segoe UI", 11), bg="#182338", fg="#ffffff", insertbackground="#00d2ff", relief="flat")
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.cmd_entry.bind("<Return>", lambda e: self._on_submit_command())

        self.mic_btn = tk.Button(
            cmd_frame,
            text="🎙️ TALK (HOLD/CLICK)",
            font=("Segoe UI", 9, "bold"),
            bg="#eb4d4b",
            fg="#ffffff",
            relief="flat",
            padx=10,
            command=self._on_voice_talk_click
        )
        self.mic_btn.pack(side="left", padx=4)

        btn = tk.Button(cmd_frame, text="DISPATCH 🚀", font=("Segoe UI", 9, "bold"), bg="#00a8ff", fg="#ffffff", relief="flat", padx=12, command=self._on_submit_command)
        btn.pack(side="right")

    def _on_voice_talk_click(self):
        """Triggered on clicking the microphone button."""
        self.mic_btn.configure(text="🔴 LISTENING...", bg="#ff7979")
        self.log_text.insert("end", "\n[VOICE]: 🎙️ Listening to microphone for 4 seconds... (Speak now!)\n")
        self.log_text.see("end")

        def _record():
            try:
                from jarvisx.voice.sovereign_wake_word_engine import get_wakeword_engine
                engine = get_wakeword_engine()
                text = engine.record_and_transcribe_manual(duration_sec=3.8)
                if text:
                    self.cmd_entry.delete(0, "end")
                    self.cmd_entry.insert(0, text)
                    self._on_submit_command()
                else:
                    self.log_text.insert("end", "[VOICE]: Inaudible speech detected. Please speak louder.\n")
                    self.log_text.see("end")
            except Exception as ex:
                self.log_text.insert("end", f"[VOICE ERROR]: {ex}\n")
                self.log_text.see("end")
            finally:
                self.mic_btn.configure(text="🎙️ TALK (HOLD/CLICK)", bg="#eb4d4b")

        threading.Thread(target=_record, daemon=True).start()


    def _start_update_loop(self):
        """Updates telemetry every 1.5 seconds."""
        def update():
            try:
                vm = psutil.virtual_memory()
                cpu_pct = psutil.cpu_percent(interval=0.05)
                
                self.cpu_var.set(f"CPU Load: {cpu_pct:.1f}%")
                self.cpu_bar["value"] = cpu_pct

                self.ram_var.set(f"RAM Utilization: {vm.percent:.1f}% ({vm.available / (1024**3):.2f} GB Free / {vm.total / (1024**3):.1f} GB Total)")
                self.ram_bar["value"] = vm.percent

                # Power
                battery = psutil.sensors_battery()
                if battery:
                    power_text = f"Power: {'AC Plugged In (100% Boost)' if battery.power_plugged else f'Battery ({battery.percent}% Eco)'}"
                else:
                    power_text = "Power: Desktop / AC Power"
                self.power_var.set(power_text)

                # Game Governor
                gov_st = self.orchestrator.game_governor.get_status()
                act = gov_st.get("active_game")
                if act:
                    self.game_var.set(f"🎮 Active Game: {act.get('game_title')} (PID {act.get('pid')})")
                    self.mode_var.set(f"Governor Mode: {act.get('current_mode')} | Target: {act.get('current_fps_target')} FPS")
                else:
                    self.game_var.set("Active Game: None (Sentinel polling every 2.5s)")
                    self.mode_var.set("Governor Policy: STANDBY_HIGH_PERFORMANCE")

                # Events log update
                events = self.orchestrator.active_events[-4:]
                if events:
                    last_ev = events[-1].get("message", "")
                    # Append if new
                    cur_text = self.log_text.get("1.0", "end")
                    if last_ev and last_ev not in cur_text:
                        self.log_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {last_ev}\n")
                        self.log_text.see("end")

            except Exception:
                pass

            self.root.after(1500, update)

        self.root.after(500, update)

    def _on_submit_command(self):
        prompt = self.cmd_entry.get().strip()
        if not prompt:
            return
        self.cmd_entry.delete(0, "end")
        self.log_text.insert("end", f"\n[USER MISSION]: {prompt}\n")
        self.log_text.insert("end", f"[ALFRED]: ⚡ Acknowledged, Sir. Processing via Groq LPU in real-time...\n")
        self.log_text.see("end")

        def run_mission():
            import asyncio

            async def _run():
                try:
                    from jarvisx.organism import get_organism
                    res = await get_organism().react_turn(prompt)
                    
                    # Log tool actions if any were taken
                    if res.get("tool"):
                        tool_st = res.get("tool_result", {}).get("status", "success")
                        self.log_text.insert("end", f"[ALFRED ACTION]: {res.get('tool')} -> {tool_st}\n")
                    
                    resp = res.get("response") or res.get("spoken") or "Mission completed."
                    self.log_text.insert("end", f"[ALFRED RESPONSE]: {resp}\n")
                    self.log_text.see("end")
                except Exception as ex:
                    err_msg = f"Mission execution notice: {ex}"
                    self.log_text.insert("end", f"[ALFRED ERROR]: {err_msg}\n")
                    self.log_text.see("end")

            asyncio.run(_run())

        threading.Thread(target=run_mission, daemon=True).start()



    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    hud = AlfredSituationRoomHUD()
    hud.run()
