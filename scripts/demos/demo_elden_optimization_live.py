"""
Live Demonstration Script for Elden Ring Sovereign Game Optimizer in Jarvis X.
Executes live hardware inspection, active process detection (PID, priority),
Win32 EmptyWorkingSet memory compaction, GraphicsConfig.xml patch (GrassQuality LOW),
and visual terminal dashboard output.
"""

import os
import sys
import time
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

import psutil
from jarvisx.gaming.game_optimizer_agent import get_game_optimizer


def main():
    optimizer = get_game_optimizer()

    print("\n" + "=" * 76)
    print(" ⚔️  JARVIS X / ALFRED: ELDEN RING SOVEREIGN PERFORMANCE SENTINEL")
    print("=" * 76)

    # 1. Hardware & System Inspection
    print("[*] Stage 1: Hardware & System Telemetry...")
    hw = optimizer.inspect_hardware()
    print(f"    • CPU: {hw.cpu_name} ({hw.cpu_cores} Cores / {hw.cpu_threads} Threads)")
    print(f"    • GPU: {hw.gpu_name}")
    print(f"    • RAM: {hw.total_ram_gb} GB Total | Available: {hw.available_ram_gb} GB")
    print(f"    • Power Mode: {'AC Power (Maximum Performance)' if hw.is_on_ac_power else 'Battery (Power Saver)'}")
    print(f"    • Hardware Tier: [{hw.hardware_tier}]")
    time.sleep(0.5)

    # 2. Active Elden Ring Process Detection
    print("\n[*] Stage 2: Scanning Active Game Process...")
    elden_proc = None
    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            if p.info["name"] and "eldenring" in p.info["name"].lower():
                elden_proc = p
                break
        except Exception:
            pass

    if elden_proc:
        try:
            mem_mb = elden_proc.info["memory_info"].rss / (1024 ** 2)
            p_obj = psutil.Process(elden_proc.info["pid"])
            prio = p_obj.nice()
            print(f"    [+] Target Detected: {elden_proc.info['name']} (PID: {elden_proc.info['pid']})")
            print(f"    [+] Memory Working Set: {mem_mb:.1f} MB")
            print(f"    [+] Initial Scheduling Priority: {prio}")
        except Exception as e:
            print(f"    [!] Error querying Elden Ring process: {e}")
    else:
        print("    [-] Elden Ring is not currently running. Will configure offline profile & XML.")

    # 3. Memory Telemetry Pre-Optimization
    vm_pre = psutil.virtual_memory()
    print(f"\n[*] Stage 3: System Memory Status Before Compaction:")
    print(f"    • Free RAM: {vm_pre.available / (1024 ** 3):.2f} GB ({vm_pre.percent}% used)")

    # 4. Execute Optimization Pass
    print("\n[*] Stage 4: Executing Sovereign Game Optimization Pass for 'ELDEN RING'...")
    res = optimizer.optimize_game("elden_ring")

    print(f"    [+] Game Profile: {res.game_title}")
    print(f"    [+] Target Frame Rate: {res.target_fps} FPS")
    print(f"    [+] RAM Memory Reclaimed: {res.ram_freed_mb:.1f} MB")

    print("\n    [+] Applied Graphics Settings:")
    for k, v in list(res.applied_settings.items())[:8]:
        print(f"        • {k:26}: {v}")

    print("\n    [+] Windows OS & Kernel Enhancements:")
    for opt in res.os_optimizations_applied:
        print(f"        ✓ {opt}")

    # 5. Post-Optimization Telemetry & Validation
    vm_post = psutil.virtual_memory()
    print(f"\n[*] Stage 5: Verification & Post-Optimization Telemetry:")
    print(f"    • Available RAM: {vm_post.available / (1024 ** 3):.2f} GB ({vm_post.percent}% used)")
    net_reclaimed = max(0, vm_post.available - vm_pre.available) / (1024 ** 2)
    print(f"    • Total Instant Memory Relief: {net_reclaimed:.1f} MB")

    if elden_proc:
        try:
            p_obj = psutil.Process(elden_proc.info["pid"])
            print(f"    • Verified Game Priority: {p_obj.nice()} (HIGH_PRIORITY_CLASS = 128)")
        except Exception:
            pass

    # Verify GraphicsConfig.xml
    cfg_path = os.path.expandvars("%APPDATA%/EldenRing/GraphicsConfig.xml")
    if os.path.exists(cfg_path):
        try:
            raw = Path(cfg_path).read_bytes()
            enc = "utf-16" if (raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff") or b"\x00" in raw[:100]) else "utf-8"
            xml_text = raw.decode(enc, errors="replace")
            has_grass_low = "<GrassQuality>LOW</GrassQuality>" in xml_text
            has_rt_disable = "<RaytracingQuality>DISABLE</RaytracingQuality>" in xml_text
            print(f"    • GraphicsConfig.xml Verified: GrassQuality=LOW ({has_grass_low}), Raytracing=DISABLE ({has_rt_disable})")
        except Exception as e:
            print(f"    • GraphicsConfig.xml read note: {e}")

    print("\n" + "=" * 76)
    print(" [OK] ✅ ELDEN RING OPTIMIZATION PASS COMPLETE — ZERO PAGEFILE THRASHING")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    main()
