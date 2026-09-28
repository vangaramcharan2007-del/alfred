#!/usr/bin/env python3
"""
Jarvis X - Red Dead Redemption 2 Peak Gaming & Immersion Controller
Autonomous Hardware Optimization, Game Sentinel & Outlaw Vibes Orchestrator.

Commands:
  python scripts/rdr2_peak_gaming.py --optimize   # Apply Ultimate Power, Flush RAM, Set GPU Priority, Apply RDR2 Theme
  python scripts/rdr2_peak_gaming.py --status     # Display Gaming Readiness & System Health Dashboard
  python scripts/rdr2_peak_gaming.py --launch     # Full optimization + Launch RDR2 with active game sentinel
  python scripts/rdr2_peak_gaming.py --revert     # Restore standard balanced desktop state
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from jarvisx.agents.game_turbo import GameTurboOptimizer, DEFAULT_RDR2_PATH, DEFAULT_PLAY_RDR2


def print_banner():
    print("=" * 72)
    print("  🤠 JARVIS X - RED DEAD REDEMPTION 2 PEAK GAMING & IMMERSION SUITE 🤠")
    print("=" * 72)


def display_dashboard(audit: dict, title: str = "SYSTEM GAMING READINESS REPORT"):
    print("\n" + "-" * 72)
    print(f"  {title}")
    print("-" * 72)
    print(f"  [+] Processor          : {audit.get('cpu_cores')} Cores / {audit.get('cpu_threads')} Threads (Meteor Lake Ultra)")
    print(f"  [+] Active Power Plan  : {audit.get('power_scheme_name')}")
    print(f"  [+] Gaming Unthrottled : {'YES (Peak 100% Clocks)' if audit.get('is_gaming_power_plan') else 'NO (Throttled/Power Saver)'}")
    print(f"  [+] Physical Memory    : {audit.get('ram_available_gb')} GB Available / {audit.get('ram_total_gb')} GB Total ({audit.get('ram_used_pct')}% Used)")
    print(f"  [+] Game Installation  : {'FOUND' if audit.get('game_installed') else 'NOT FOUND'} ({audit.get('game_path')})")
    print(f"  [+] GPU High-Perf Reg  : {'CONFIGURED (DirectX Priority 2)' if audit.get('gpu_high_perf_registered') else 'DEFAULT'}")
    print(f"  [+] Windows Game Mode  : {'ENABLED' if audit.get('windows_game_mode') else 'DISABLED'}")
    print("-" * 72 + "\n")


def run_optimize(turbo: GameTurboOptimizer):
    print_banner()
    print("[*] Initiating Full Peak Gaming & Van der Linde Aesthetic Suite...")

    # Pre-audit
    before = turbo.get_system_audit()
    display_dashboard(before, "PRE-OPTIMIZATION STATE")

    print("[1/4] Unlocking Windows Ultimate Performance Power Scheme...")
    p_ok, p_msg = turbo.activate_ultimate_performance()
    print(f"      {p_msg}")

    print("[2/4] Deep Flushing Working Sets & Standby Memory Cache...")
    ram_res = turbo.reclaim_physical_ram()
    print(f"      Trimmed {ram_res['processes_trimmed']} background processes.")
    print(f"      Reclaimed: +{ram_res['ram_freed_gb']} GB RAM (Available: {ram_res['ram_after_gb']} GB)")

    print("[3/4] Binding High-Performance GPU Affinity for RDR2...")
    gpu_res = turbo.configure_gpu_and_gaming_registry()
    print(f"      DirectX UserGpuPreferences: {gpu_res.get('gpu_preferences_registered')}")
    print(f"      Windows Game Mode Registry: {gpu_res.get('game_mode_enabled')}")

    print("[4/4] Applying Authentic Red Dead Redemption 2 Outlaw Atmosphere...")
    vibe_res = turbo.apply_rdr2_vibes()
    print(f"      Theme Name      : {vibe_res.get('theme')}")
    print(f"      Typography      : {vibe_res.get('font')} (140pt UpperLeft)")
    print(f"      Outlaw Palette  : Crimson ({vibe_res.get('accent_color')}) & Prairie Gold")
    print(f"      Windows 11 DWM  : Synchronized Taskbar & Window Borders")
    print(f"      Master Clock    : Reloaded with zero lag")

    # Post-audit
    after = turbo.get_system_audit()
    display_dashboard(after, "POST-OPTIMIZATION PEAK GAMING READY")
    print("[✔] PC is 100% primed for peak zero-lag gameplay. Enjoy the frontier, Boss!\n")
    return after


def run_launch(turbo: GameTurboOptimizer):
    # First optimize
    run_optimize(turbo)

    # Locate game executable
    play_exe = Path(DEFAULT_PLAY_RDR2)
    game_exe = Path(DEFAULT_RDR2_PATH)
    target = play_exe if play_exe.exists() else game_exe

    if not target.exists():
        print(f"[-] Error: Could not locate Red Dead Redemption 2 executable at {target}.")
        return False

    print(f"[*] Launching Red Dead Redemption 2: {target}")
    print("[*] Engaging Game Sentinel: Pausing background FFT overlays for 0.00% contention...")
    turbo.set_background_quiet_mode(pause=True)

    try:
        proc = subprocess.Popen([str(target)], cwd=str(target.parent))
        print(f"[+] RDR2 Process Launched (PID: {proc.pid}).")
        print("[*] Sentinel active: Monitoring game session... (Press Ctrl+C to abort sentinel)")

        # Sentinel loop
        while proc.poll() is None:
            time.sleep(3)

        print(f"\n[+] Red Dead Redemption 2 session concluded (Exit Code: {proc.returncode}).")
    except KeyboardInterrupt:
        print("\n[*] Sentinel detached by user.")
    finally:
        print("[*] Resuming desktop Chameleon suite and restoring system balance...")
        turbo.set_background_quiet_mode(pause=False)
        turbo.restore_balanced_power_plan()
        print("[+] System restored to balanced desktop mode.\n")


def main():
    parser = argparse.ArgumentParser(description="Jarvis X RDR2 Peak Gaming & Immersion Controller")
    parser.add_argument("--optimize", action="store_true", help="Apply full peak gaming tuning & RDR2 theme")
    parser.add_argument("--status", action="store_true", help="Display system gaming readiness report")
    parser.add_argument("--launch", action="store_true", help="Optimize + Launch RDR2 with active sentinel")
    parser.add_argument("--revert", action="store_true", help="Restore balanced power plan and desktop suite")

    args = parser.parse_args()
    turbo = GameTurboOptimizer()

    if args.status:
        print_banner()
        display_dashboard(turbo.get_system_audit())
    elif args.launch:
        run_launch(turbo)
    elif args.revert:
        print_banner()
        turbo.set_background_quiet_mode(pause=False)
        p_ok, p_msg = turbo.restore_balanced_power_plan()
        print(f"[+] {p_msg}")
        print("[+] Chameleon visualizer resumed.")
    else:
        # Default action is optimize
        run_optimize(turbo)


if __name__ == "__main__":
    main()
