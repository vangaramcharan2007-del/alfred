"""
Live Demonstration Script for Alfred Sovereign Gaming Optimizer Agent.
Executes live hardware telemetry inspection, game graphics synthesis, Windows priority tuning,
and terminal HUD visualization.
"""

import os
import sys
import time

# Ensure UTF-8 output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

from jarvisx.gaming.game_optimizer_agent import get_game_optimizer


def main():
    optimizer = get_game_optimizer()

    print("\n" + "=" * 70)
    print(" 🎮 ALFRED SOVEREIGN GAMING OPTIMIZATION SENTINEL (LIVE HUD)")
    print("=" * 70)

    # 1. Hardware Inspection
    print("[*] Stage 1: Inspecting Host Laptop Hardware & Thermal Profile...")
    hw = optimizer.inspect_hardware()
    print(f"    • CPU: {hw.cpu_name} ({hw.cpu_cores} Cores / {hw.cpu_threads} Threads)")
    print(f"    • GPU: {hw.gpu_name}")
    print(f"    • RAM: {hw.total_ram_gb} GB Total ({hw.available_ram_gb} GB Available)")
    print(f"    • Power Status: {'AC Plugged In (Full Performance Mode)' if hw.is_on_ac_power else 'Battery (Eco-Thermal Mode)'}")
    print(f"    • Computed Hardware Tier: [{hw.hardware_tier}]")
    time.sleep(1.0)

    # 2. Optimize Sample Games (Competitive vs Open World vs AAA)
    sample_games = ["valorant", "gtav", "cyberpunk2077"]

    for g in sample_games:
        print("\n" + "-" * 70)
        print(f"[*] Stage 2: Autonomous Optimization Pass for '{g.upper()}'...")
        res = optimizer.optimize_game(g)
        
        print(f"    [+] Game Identified: {res.game_title}")
        print(f"    [+] Target FPS Objective: {res.target_fps} FPS")
        print(f"    [+] RAM Memory Reclaimed: {res.ram_freed_mb:.1f} MB")
        
        print("    [+] Adapted Optimal Graphics Profile:")
        for k, v in list(res.applied_settings.items())[:6]:
            print(f"        • {k:25}: {v}")
            
        print("    [+] Windows OS & Kernel Enhancements Applied:")
        for opt in res.os_optimizations_applied:
            print(f"        ✓ {opt}")
            
        time.sleep(0.8)

    print("\n" + "=" * 70)
    print(" [OK] ✅ GAMING AGENT SYSTEM FULLY ACTIVE & OPERATIONAL UNDER ALFRED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
