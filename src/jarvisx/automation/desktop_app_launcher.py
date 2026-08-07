"""Jarvis X Desktop HUD & Voice Interactive Application Launcher.

Launches the top-most Desktop HUD Companion UI, speaks out loud via TTS,
and activates F.R.I.D.A.Y. tactical mode telemetry.
"""

import sys
import os
import time
import subprocess

# Ensure src is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.automation.native_companion_ui import NativeCompanionUI
from jarvisx.automation.friday_tactical_mode import FridayTacticalMode
from jarvisx.automation.real_voice_runtime import RealVoiceRuntime


def launch_desktop_hud_and_voice():
    """Launch the top-most floating Desktop HUD window and speak via TTS."""
    print("=" * 50)
    print("  LAUNCHING F.R.I.D.A.Y. DESKTOP HUD & VOICE APP")
    print("=" * 50)

    kernel = PersonalOSKernel()
    friday = FridayTacticalMode(theme="CYAN_HOLOGRAPHIC_TACTICAL")
    voice = RealVoiceRuntime()

    # 1. Activate F.R.I.D.A.Y. tactical sweep
    sweep_res = friday.activate_tactical_sweep(os_kernel=kernel)
    print(f"\n[1/3] F.R.I.D.A.Y. Sweep: {sweep_res['status']} ({sweep_res['persona']})")

    # 2. Trigger TTS speech out loud
    speech_text = "F.R.I.D.A.Y. Tactical Mode Active, Boss. Desktop HUD widget and voice pipeline online."
    print(f"\n[2/3] Speaking via TTS: '{speech_text}'")
    
    # Try SAPI PowerShell TTS directly for guaranteed desktop audio output
    try:
        ps_cmd = f"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Volume = 100; $s.Speak('{speech_text}')"
        subprocess.Popen(["powershell", "-Command", ps_cmd], shell=False)
    except Exception:
        voice.speak_response(speech_text)

    # 3. Launch Desktop HUD Tkinter Window directly in main thread
    print("\n[3/3] Displaying Top-Most Desktop HUD Floating Widget Window...")
    gui = NativeCompanionUI(os_kernel=kernel)
    
    if sys.platform.startswith("win"):
        try:
            import tkinter as tk
            root = tk.Tk()
            root.title("F.R.I.D.A.Y. Tactical HUD")
            root.geometry("360x220+1150+60")
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.configure(bg="#090d16")

            # Border frame
            border = tk.Frame(root, bg="#00f0ff", bd=1)
            border.pack(fill="both", expand=True)

            inner = tk.Frame(border, bg="#090d16")
            inner.pack(fill="both", expand=True, padx=2, pady=2)

            title_lbl = tk.Label(
                inner,
                text="⚡ F.R.I.D.A.Y. TACTICAL HUD",
                font=("Segoe UI", 11, "bold"),
                fg="#00f0ff",
                bg="#090d16",
            )
            title_lbl.pack(pady=8)

            stat = gui.build_status_dict()
            info_text = (
                f"• Persona: F.R.I.D.A.Y. Tactical\n"
                f"• Theme: Cyan Holographic\n"
                f"• System Status: ONLINE (+{stat['hspw']} HSPW)\n"
                f"• Active Priority: {stat['top_priority'][:28]}"
            )
            info_lbl = tk.Label(
                inner,
                text=info_text,
                font=("Segoe UI", 9),
                fg="#c9d1d9",
                bg="#090d16",
                justify="left",
            )
            info_lbl.pack(pady=6)

            btn_frame = tk.Frame(inner, bg="#090d16")
            btn_frame.pack(pady=8)

            clean_btn = tk.Button(
                btn_frame,
                text="Clean PC",
                font=("Segoe UI", 9, "bold"),
                bg="#238636",
                fg="#ffffff",
                relief="flat",
                command=lambda: kernel.execute_objective("clean pc"),
            )
            clean_btn.pack(side="left", padx=6)

            dismiss_btn = tk.Button(
                btn_frame,
                text="Dismiss HUD",
                font=("Segoe UI", 9),
                bg="#21262d",
                fg="#8b949e",
                relief="flat",
                command=root.destroy,
            )
            dismiss_btn.pack(side="left", padx=6)

            root.mainloop()
        except Exception as e:
            print(f"HUD Window fallback execution: {e}")


if __name__ == "__main__":
    launch_desktop_hud_and_voice()
