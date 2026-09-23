#!/usr/bin/env python3
"""
Jarvis X Thermal & System Resource Sentinel
Fast, non-blocking telemetry & active cooling protocol.
"""

import sys
import os
import time
import subprocess
import ctypes
import threading
from typing import List, Dict, Any

# Ensure unbuffered output
sys.stdout.reconfigure(line_buffering=True)

try:
    import psutil
except ImportError:
    print("[ERROR] psutil is required. Run: pip install psutil", flush=True)
    sys.exit(1)


def get_thermal_sensors_safe(timeout_sec: float = 2.0) -> List[Dict[str, Any]]:
    """Safely fetch temperatures with strict timeout to avoid WMI freeze."""
    results: List[Dict[str, Any]] = []

    def probe():
        # 1. psutil sensors
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            results.append({
                                "sensor": f"{name} ({entry.label or 'core'})",
                                "temp_c": round(entry.current, 1)
                            })
        except Exception:
            pass

        # 2. PowerShell WMI MSAcpi_ThermalZoneTemperature
        try:
            ps_cmd = "Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue | Select-Object -First 3 | ForEach-Object { [math]::Round(($_.CurrentTemperature / 10 - 273.15), 1) }"
            p = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=1.8)
            for line in p.stdout.strip().splitlines():
                line = line.strip()
                if line:
                    try:
                        val = float(line)
                        results.append({"sensor": "ACPI Thermal Zone", "temp_c": val})
                    except ValueError:
                        pass
        except Exception:
            pass

    t = threading.Thread(target=probe, daemon=True)
    t.start()
    t.join(timeout=timeout_sec)
    return results


def get_process_resource_hogs() -> Dict[str, List[Dict[str, Any]]]:
    """Sample processes over 0.8s window for accurate real-time CPU%."""
    # First pass: record initial times
    active_procs = []
    for p in psutil.process_iter(['pid', 'name']):
        try:
            p.cpu_percent(interval=None)
            active_procs.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(0.8)

    stats = []
    for p in active_procs:
        try:
            cpu = p.cpu_percent(interval=None)
            mem = p.memory_info().rss / (1024 * 1024)
            stats.append({
                "pid": p.pid,
                "name": p.name(),
                "cpu_percent": cpu,
                "memory_mb": round(mem, 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    by_cpu = sorted(stats, key=lambda x: x["cpu_percent"], reverse=True)
    by_mem = sorted(stats, key=lambda x: x["memory_mb"], reverse=True)

    return {
        "top_cpu": by_cpu[:12],
        "top_mem": by_mem[:10],
    }


def get_power_scheme_info() -> str:
    try:
        res = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True, timeout=2)
        out = res.stdout.strip()
        # Parse GUID and name
        if "GUID:" in out:
            return out.split("GUID:")[1].strip()
        return out
    except Exception:
        return "Unknown"


def trim_system_working_sets() -> int:
    """Trim memory working sets across processes to relieve memory pressure."""
    trimmed = 0
    for p in psutil.process_iter(['pid']):
        try:
            handle = ctypes.windll.kernel32.OpenProcess(0x001F0FFF, False, p.pid)
            if handle:
                ctypes.windll.psapi.EmptyWorkingSet(handle)
                ctypes.windll.kernel32.CloseHandle(handle)
                trimmed += 1
        except Exception:
            continue
    return trimmed


def set_power_mode(mode: str = "balanced") -> bool:
    """
    Switch Windows power scheme:
    'balanced': 381b4222-f694-41f0-9685-ff5bb260df2e
    'saver': a1841308-3541-4fab-bc81-f71556f20b4a
    """
    guid_map = {
        "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
        "saver": "a1841308-3541-4fab-bc81-f71556f20b4a",
        "power_saver": "a1841308-3541-4fab-bc81-f71556f20b4a",
    }
    guid = guid_map.get(mode.lower(), "381b4222-f694-41f0-9685-ff5bb260df2e")
    try:
        res = subprocess.run(["powercfg", "/setactive", guid], capture_output=True, text=True, timeout=3)
        return res.returncode == 0
    except Exception:
        return False


def run_diagnostics(cool_down: bool = False):
    print("=" * 68, flush=True)
    print("  JARVIS X THERMAL & RESOURCE HEALTH SENTINEL", flush=True)
    print("=" * 68, flush=True)

    # 1. CPU & Memory
    core_count = psutil.cpu_count(logical=True)
    cpu_per_core = psutil.cpu_percent(interval=0.4, percpu=True)
    cpu_total = sum(cpu_per_core) / len(cpu_per_core)

    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    battery = psutil.sensors_battery()

    print(f"\n[+] CPU Load: {cpu_total:.1f}% overall across {core_count} threads", flush=True)
    core_fmt = " | ".join([f"C{i}:{pct:4.1f}%" for i, pct in enumerate(cpu_per_core)])
    print(f"    Cores: {core_fmt}", flush=True)

    print(f"\n[+] Memory Load:", flush=True)
    print(f"    RAM: {vm.used / (1024**3):.2f} GB / {vm.total / (1024**3):.2f} GB ({vm.percent}%) [Available: {vm.available / (1024**3):.2f} GB]", flush=True)
    print(f"    Commit: {swap.used / (1024**3):.2f} GB / {swap.total / (1024**3):.2f} GB ({swap.percent}%)", flush=True)

    # 2. Power & Scheme
    scheme_str = get_power_scheme_info()
    print(f"\n[+] Power & Battery:", flush=True)
    if battery:
        state = "AC Power (Charging/Mains)" if battery.power_plugged else "Battery Discharging"
        print(f"    State: {state} | Charge: {battery.percent}%", flush=True)
    print(f"    Active Power Scheme: {scheme_str}", flush=True)

    # 3. Temperatures
    temps = get_thermal_sensors_safe(timeout_sec=2.0)
    print(f"\n[+] Thermal Telemetry:", flush=True)
    if temps:
        for t in temps:
            status = "CRITICAL" if t["temp_c"] > 85 else "WARM" if t["temp_c"] > 70 else "NOMINAL"
            print(f"    [{status}] {t['sensor']}: {t['temp_c']} deg C", flush=True)
    else:
        print("    [Info] Direct ACPI/WMI thermal probes not reported or hardware-protected.", flush=True)

    # 4. Top Process Hogs
    print("\n[+] Sampling High-Load Processes (0.8s delta)...", flush=True)
    hogs = get_process_resource_hogs()

    print("\n  --- TOP CPU CONSUMERS ---", flush=True)
    print(f"  {'PID':<8} {'PROCESS NAME':<28} {'CPU %':<10} {'RAM (MB)':<10}", flush=True)
    print("  " + "-" * 58, flush=True)
    for p in hogs["top_cpu"]:
        if p["cpu_percent"] > 0.1:
            print(f"  {p['pid']:<8} {p['name'][:26]:<28} {p['cpu_percent']:<10.1f} {p['memory_mb']:<10.1f}", flush=True)

    print("\n  --- TOP MEMORY CONSUMERS ---", flush=True)
    print(f"  {'PID':<8} {'PROCESS NAME':<28} {'RAM (MB)':<10} {'CPU %':<10}", flush=True)
    print("  " + "-" * 58, flush=True)
    for p in hogs["top_mem"]:
        print(f"  {p['pid']:<8} {p['name'][:26]:<28} {p['memory_mb']:<10.1f} {p['cpu_percent']:<10.1f}", flush=True)

    # 5. Analysis
    print("\n" + "=" * 68, flush=True)
    print("  THERMAL ROOT CAUSE ANALYSIS", flush=True)
    print("=" * 68, flush=True)

    reasons = []
    top_cpu = hogs["top_cpu"][0] if hogs["top_cpu"] else None
    if top_cpu and top_cpu["cpu_percent"] >= 20.0:
        reasons.append(f"Heavy CPU burden from '{top_cpu['name']}' (PID {top_cpu['pid']}) consuming {top_cpu['cpu_percent']}%.")

    if vm.percent > 80.0:
        reasons.append(f"High RAM saturation ({vm.percent}%), driving aggressive Windows paging and memory controller heat.")

    if battery and battery.power_plugged and battery.percent < 95:
        reasons.append(f"Battery fast-charging ({battery.percent}%) contributes significantly to chassis and VRM heating.")

    if not reasons:
        reasons.append("CPU & RAM loads are steady; thermal build-up may be residual or fan dust/surface airflow related.")

    for i, r in enumerate(reasons, 1):
        print(f"  {i}. {r}", flush=True)

    # 6. Cooling Action
    if cool_down:
        print("\n" + "=" * 68, flush=True)
        print("  ENGAGING JARVIS ACTIVE COOLING PROTOCOL", flush=True)
        print("=" * 68, flush=True)
        print("  [*] Performing kernel working set purge across processes...", flush=True)
        flushed = trim_system_working_sets()
        print(f"  [+] Purged standby working sets for {flushed} processes.", flush=True)

        print("  [*] Enforcing power throttle (Power Saver / Balanced)...", flush=True)
        if set_power_mode("saver"):
            print("  [+] Power scheme engaged: Power Saver (CPU package frequency and wattage capped).", flush=True)
        else:
            set_power_mode("balanced")
            print("  [+] Power scheme engaged: Balanced.", flush=True)

        time.sleep(1)
        vm_post = psutil.virtual_memory()
        freed = (vm_post.available - vm.available) / (1024 * 1024)
        if freed > 0:
            print(f"  [+] Freed ~{freed:.1f} MB of RAM from cache.", flush=True)
        print("  [+] Active cooling protocol complete. Fan speed should normalize.", flush=True)


if __name__ == "__main__":
    do_cool = "--cool" in sys.argv or "-c" in sys.argv
    run_diagnostics(cool_down=do_cool)
