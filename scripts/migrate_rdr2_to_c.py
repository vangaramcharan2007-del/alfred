#!/usr/bin/env python3
"""
Jarvis X - RDR2 Fast SSD Migration & Configuration Engine
Transfers Red Dead Redemption 2 from external HDD (F:) to internal PCIe NVMe SSD (C:)
with multi-threaded Robocopy, verifies data integrity, and updates all system shortcuts.

Usage:
  python scripts/migrate_rdr2_to_c.py
"""

import os
import sys
import time
import shutil
import winreg
import subprocess
from pathlib import Path

SOURCE_DIR = Path(r"F:\Games\Red Dead Redemption 2")
DEST_DIR = Path(r"C:\Games\Red Dead Redemption 2")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def verify_source():
    if not SOURCE_DIR.exists():
        print(f"[-] Error: Source directory {SOURCE_DIR} not found. Ensure Drive F: is connected.")
        return False
    if not (SOURCE_DIR / "RDR2.exe").exists():
        print(f"[-] Error: RDR2.exe not found in {SOURCE_DIR}.")
        return False
    return True


def check_destination_space():
    DEST_DIR.parent.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage("C:")
    free_gb = usage.free / (1024**3)
    print(f"[*] Drive C: Free Space: {free_gb:.2f} GB (Required: ~117 GB)")
    if free_gb < 118.0:
        print(f"[-] Warning: Drive C: has only {free_gb:.2f} GB free, which is very tight.")
        return False
    return True


def run_robocopy_transfer():
    print("=" * 70)
    print("  [MIGRATE] JARVIS X - RDR2 HIGH-SPEED NVMe SSD MIGRATION")
    print("=" * 70)
    print(f"  [+] Source Path      : {SOURCE_DIR}")

    print(f"  [+] Destination Path : {DEST_DIR}")
    print(f"  [+] Transfer Engine  : Windows Multi-Threaded Robocopy (16 threads)")
    print("=" * 70 + "\n")

    start_time = time.time()
    cmd = [
        "robocopy",
        str(SOURCE_DIR),
        str(DEST_DIR),
        "/E",          # Copy subdirectories, including empty ones
        "/MT:16",      # 16-thread multi-threaded copy
        "/R:2",        # Retry twice on error
        "/W:2",        # Wait 2 seconds between retries
        "/NFL",        # No file log (keeps output clean)
        "/NDL",        # No directory log
        "/NP"          # No progress percentage flood
    ]

    print("[*] Initiating high-speed stream transfer... (Estimated: 15-20 min)")
    # Note: Robocopy returns codes 0-7 on success (1 = files copied, 0 = no files copied)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Monitor transfer in progress
    while process.poll() is None:
        time.sleep(5)
        if DEST_DIR.exists():
            try:
                dest_usage = sum(f.stat().st_size for f in DEST_DIR.rglob('*') if f.is_file()) / (1024**3)
                elapsed = time.time() - start_time
                speed_mbs = (dest_usage * 1024) / max(elapsed, 1.0)
                pct = min(100.0, (dest_usage / 116.83) * 100.0)
                print(f"    --> Transferred: {dest_usage:.2f} GB / 116.83 GB ({pct:.1f}%) | Avg Speed: {speed_mbs:.1f} MB/s | Elapsed: {elapsed/60:.1f} min", end="\r", flush=True)
            except Exception:
                pass

    returncode = process.returncode
    elapsed_total = time.time() - start_time
    print(f"\n[+] Robocopy completed in {elapsed_total / 60:.2f} minutes (Exit code: {returncode}).")
    
    # In Robocopy, exit codes < 8 indicate success
    return returncode < 8


def verify_integrity():
    print("[*] Verifying file integrity on Drive C:...")
    src_files = {p.relative_to(SOURCE_DIR): p.stat().st_size for p in SOURCE_DIR.rglob('*') if p.is_file()}
    dest_files = {p.relative_to(DEST_DIR): p.stat().st_size for p in DEST_DIR.rglob('*') if p.is_file()}

    missing = set(src_files.keys()) - set(dest_files.keys())
    if missing:
        print(f"[-] Integrity Failure: {len(missing)} files missing on C:!")
        return False

    size_mismatches = [k for k in src_files if src_files[k] != dest_files.get(k)]
    if size_mismatches:
        print(f"[-] Integrity Failure: {len(size_mismatches)} files have size mismatches!")
        return False

    total_dest_gb = sum(dest_files.values()) / (1024**3)
    print(f"[OK] Integrity Verified: All {len(dest_files)} files intact on C: ({total_dest_gb:.2f} GB).")
    return True


def update_system_bindings():
    print("[*] Updating system shortcuts and GPU affinity for C: drive installation...")
    c_rdr2 = DEST_DIR / "RDR2.exe"
    c_play = DEST_DIR / "PlayRDR2.exe"

    # 1. Update DirectX UserGpuPreferences in Registry
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\DirectX\UserGpuPreferences")
        winreg.SetValueEx(key, str(c_rdr2), 0, winreg.REG_SZ, "GpuPreference=2;")
        if c_play.exists():
            winreg.SetValueEx(key, str(c_play), 0, winreg.REG_SZ, "GpuPreference=2;")
        winreg.CloseKey(key)
        print("[+] DirectX UserGpuPreferences bound to High Performance GPU on C:.")
    except Exception as e:
        print(f"[-] Warning: Could not update DirectX GPU registry: {e}")

    # 2. Update Desktop Shortcut
    try:
        desktop_dir = Path.home() / "Desktop"
        shortcut_path = desktop_dir / "Play Red Dead Redemption 2 (Turbo Mode).lnk"
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        target_exe = c_play if c_play.exists() else c_rdr2
        shortcut.Targetpath = str(target_exe)
        shortcut.WorkingDirectory = str(DEST_DIR)
        shortcut.IconLocation = str(target_exe) + ", 0"
        shortcut.Description = "Play Red Dead Redemption 2 (Peak NVMe SSD Turbo Mode)"
        shortcut.save()
        print(f"[+] Desktop Shortcut updated to launch directly from C: NVMe SSD.")
    except Exception as e:
        print(f"[-] Warning: Could not update desktop shortcut: {e}")


def main():
    if not verify_source():
        sys.exit(1)
    if not check_destination_space():
        sys.exit(1)

    success = run_robocopy_transfer()
    if not success:
        print("[-] Error: Robocopy transfer encountered critical issues.")
        sys.exit(1)

    if verify_integrity():
        update_system_bindings()
        print("\n" + "=" * 70)
        print("  [SUCCESS] MIGRATION COMPLETE! RED DEAD REDEMPTION 2 IS NOW ON NVMe SSD!")
        print("=" * 70)
        print("  1. You can now UNPLUG your external hard drive (Drive F:) completely.")
        print("  2. Plug your cooling pad directly into your laptop's USB port.")
        print("  3. Double-click the desktop shortcut to play at peak NVMe speed!")
        print("=" * 70 + "\n")
    else:
        print("[-] Data verification failed. Please check the logs.")



if __name__ == "__main__":
    main()
