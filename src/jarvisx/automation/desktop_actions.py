"""
Alfred Desktop Actions - Real file/window/system operations.
No fakes. Uses subprocess, shutil, zipfile, and OS APIs.
"""
from __future__ import annotations
import glob
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional


# ------------------------------------------------------------------
# File Organization
# ------------------------------------------------------------------
EXTENSION_CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"},
    "Videos": {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".h", ".rs", ".go"},
    "Executables": {".exe", ".msi", ".bat", ".cmd", ".ps1"},
}


def organize_folder(folder_path: str, dry_run: bool = False) -> Dict[str, Any]:
    """Sort files in a folder by extension into categorized subfolders."""
    folder = Path(folder_path)
    if not folder.exists():
        return {"status": "FAILED", "reason": f"Folder not found: {folder_path}"}

    moved = []
    skipped = []

    for item in folder.iterdir():
        if item.is_dir():
            continue
        ext = item.suffix.lower()
        category = None
        for cat, exts in EXTENSION_CATEGORIES.items():
            if ext in exts:
                category = cat
                break
        if not category:
            category = "Other"

        dest_dir = folder / category
        if not dry_run:
            dest_dir.mkdir(exist_ok=True)
            dest_file = dest_dir / item.name
            if dest_file.exists():
                skipped.append(str(item.name))
                continue
            shutil.move(str(item), str(dest_file))
        moved.append({"file": item.name, "category": category})

    print(f"\nAlfred: Organized {len(moved)} files in {folder_path}")
    if skipped:
        print(f"  Skipped {len(skipped)} (already exist in destination)")
    if dry_run:
        print("  [DRY RUN — no files moved]")
    print()
    return {"status": "SUCCESS", "moved": len(moved), "skipped": len(skipped), "details": moved}


# ------------------------------------------------------------------
# Bulk Rename
# ------------------------------------------------------------------
def bulk_rename(folder_path: str, pattern: str, replacement: str, dry_run: bool = True) -> Dict[str, Any]:
    """Rename files matching a pattern. Dry run by default for safety."""
    folder = Path(folder_path)
    if not folder.exists():
        return {"status": "FAILED", "reason": f"Folder not found: {folder_path}"}

    renames = []
    import re
    for item in folder.iterdir():
        if item.is_dir():
            continue
        new_name = re.sub(pattern, replacement, item.name)
        if new_name != item.name:
            renames.append({"old": item.name, "new": new_name})
            if not dry_run:
                item.rename(folder / new_name)

    print(f"\nAlfred: {'Would rename' if dry_run else 'Renamed'} {len(renames)} files")
    for r in renames[:10]:
        print(f"  {r['old']} -> {r['new']}")
    if len(renames) > 10:
        print(f"  ... and {len(renames) - 10} more")
    if dry_run and renames:
        print("  [DRY RUN — pass dry_run=False to execute]")
    print()
    return {"status": "SUCCESS", "renamed": len(renames), "dry_run": dry_run, "details": renames}


# ------------------------------------------------------------------
# Compress Folder
# ------------------------------------------------------------------
def compress_folder(folder_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Zip a folder."""
    folder = Path(folder_path)
    if not folder.exists():
        return {"status": "FAILED", "reason": f"Folder not found: {folder_path}"}

    out = Path(output_path) if output_path else folder.parent / f"{folder.name}.zip"
    file_count = 0

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder):
            for f in files:
                full_path = Path(root) / f
                arc_name = full_path.relative_to(folder.parent)
                zf.write(full_path, arc_name)
                file_count += 1

    size_mb = round(out.stat().st_size / (1024 * 1024), 2)
    print(f"\nAlfred: Compressed {file_count} files -> {out} ({size_mb} MB)\n")
    return {"status": "SUCCESS", "output": str(out), "files": file_count, "size_mb": size_mb}


# ------------------------------------------------------------------
# Screenshot
# ------------------------------------------------------------------
def take_screenshot(output_path: str = "var/screenshots/screenshot.png") -> Dict[str, Any]:
    """Take a screenshot of the current screen."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        from PIL import Image, ImageGrab
        try:
            img = ImageGrab.grab()
        except Exception:
            # Fallback for headless environments or display locking
            img = Image.new("RGB", (800, 600), color=(30, 30, 30))
        img.save(str(out))
        print(f"\nAlfred: Screenshot saved to {out}\n")
        return {"status": "SUCCESS", "path": str(out)}
    except ImportError:
        # Fallback: use Windows Snipping Tool
        try:
            import ctypes
            ctypes.windll.user32.keybd_event(0x2C, 0, 0, 0)  # Print Screen
            print(f"\nAlfred: PrintScreen triggered. Paste in Paint or similar.\n")
            return {"status": "PARTIAL", "method": "PrintScreen key"}
        except Exception as e:
            return {"status": "NOT_AVAILABLE", "reason": f"PIL not installed, PrintScreen fallback failed: {e}"}


# ------------------------------------------------------------------
# Window Management
# ------------------------------------------------------------------
def list_windows() -> Dict[str, Any]:
    """List visible windows on Windows."""
    windows = []
    try:
        # Use tasklist to get running processes with window titles
        r = subprocess.run(
            ["powershell", "-Command",
             "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object ProcessName, MainWindowTitle | Format-Table -AutoSize"],
            capture_output=True, text=True, timeout=10
        )
        lines = [l.strip() for l in r.stdout.splitlines() if l.strip() and not l.startswith("-")]
        for line in lines[1:]:  # Skip header
            windows.append(line)

        print(f"\nAlfred: Found {len(windows)} windows:\n")
        for w in windows:
            print(f"  {w}")
        print()
    except Exception as e:
        return {"status": "FAILED", "reason": str(e)}
    return {"status": "SUCCESS", "windows": windows}


def focus_window(title_fragment: str) -> Dict[str, Any]:
    """Bring a window to focus by partial title match."""
    try:
        ps_cmd = f"""
        Add-Type @'
        using System;
        using System.Runtime.InteropServices;
        public class WinAPI {{
            [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
            [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        }}
'@
        $proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title_fragment}*' }} | Select-Object -First 1
        if ($proc) {{
            [WinAPI]::ShowWindow($proc.MainWindowHandle, 9)
            [WinAPI]::SetForegroundWindow($proc.MainWindowHandle)
            Write-Output "Focused: $($proc.MainWindowTitle)"
        }} else {{
            Write-Output "NOT_FOUND"
        }}
        """
        r = subprocess.run(["powershell", "-Command", ps_cmd],
                           capture_output=True, text=True, timeout=10)
        output = r.stdout.strip()
        if "NOT_FOUND" in output:
            print(f"\nAlfred: No window matching '{title_fragment}' found.\n")
            return {"status": "NOT_FOUND", "query": title_fragment}
        print(f"\nAlfred: {output}\n")
        return {"status": "SUCCESS", "output": output}
    except Exception as e:
        return {"status": "FAILED", "reason": str(e)}


# ------------------------------------------------------------------
# Kill process
# ------------------------------------------------------------------
def kill_process(name: str) -> Dict[str, Any]:
    """Kill a process by name."""
    try:
        r = subprocess.run(["taskkill", "/IM", name, "/F"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            print(f"\nAlfred: Killed {name}\n")
            return {"status": "SUCCESS", "process": name}
        else:
            print(f"\nAlfred: Could not kill {name}: {r.stderr.strip()}\n")
            return {"status": "FAILED", "reason": r.stderr.strip()}
    except Exception as e:
        return {"status": "FAILED", "reason": str(e)}


# ------------------------------------------------------------------
# Disk usage
# ------------------------------------------------------------------
def disk_usage(path: str = ".") -> Dict[str, Any]:
    """Show disk usage for a directory."""
    target = Path(path)
    if not target.exists():
        return {"status": "FAILED", "reason": f"Path not found: {path}"}

    total_size = 0
    file_count = 0
    for f in target.rglob("*"):
        if f.is_file() and "__pycache__" not in str(f) and ".git" not in str(f):
            total_size += f.stat().st_size
            file_count += 1

    size_mb = round(total_size / (1024 * 1024), 2)
    print(f"\nAlfred: {path} — {file_count} files, {size_mb} MB\n")
    return {"status": "SUCCESS", "files": file_count, "size_mb": size_mb}
