"""
Alfred / Jarvis X Automated Backup to Drive F:
Takes a clean, timestamped archive of the Alfred repository, databases, and configuration
and stores it safely on external drive F:\Alfred_Backups.
"""

import os
import sys
import time
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = Path("F:/Alfred_Backups")

# Ignore patterns for clean backup
EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".cache",
}

EXCLUDE_EXTS = {
    ".pyc",
    ".pyo",
    ".tmp",
}

def calculate_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def run_backup():
    print("=" * 60)
    print("       ALFRED / JARVIS X SECURE BACKUP TO DRIVE F:")
    print("=" * 60)

    if not Path("F:/").exists():
        print("[ERROR] Target drive F: is not mounted or accessible.")
        return False

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"alfred_snapshot_{timestamp}.zip"
    backup_path = BACKUP_DIR / backup_filename

    print(f"[*] Source:      {REPO_ROOT}")
    print(f"[*] Destination: {backup_path}")
    print("[*] Scanning files and building archive...")

    start_time = time.time()
    file_count = 0
    total_bytes = 0

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(REPO_ROOT):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in EXCLUDE_EXTS:
                    continue

                rel_path = file_path.relative_to(REPO_ROOT)
                try:
                    zipf.write(file_path, arcname=rel_path)
                    file_count += 1
                    total_bytes += file_path.stat().st_size
                except Exception as e:
                    print(f"    [WARN] Skipped {rel_path}: {e}")

    duration = time.time() - start_time
    archive_size_mb = backup_path.stat().st_size / (1024 * 1024)
    sha256_hash = calculate_sha256(backup_path)

    # Write manifest
    manifest_path = BACKUP_DIR / f"manifest_{timestamp}.txt"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(f"Archive: {backup_filename}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Files Archived: {file_count}\n")
        f.write(f"Uncompressed Size: {total_bytes / (1024 * 1024):.2f} MB\n")
        f.write(f"Compressed Archive Size: {archive_size_mb:.2f} MB\n")
        f.write(f"Duration: {duration:.2f} seconds\n")
        f.write(f"SHA256: {sha256_hash}\n")

    print(f"[+] Backup completed successfully in {duration:.1f}s!")
    print(f"[+] Archived {file_count} files ({archive_size_mb:.2f} MB)")
    print(f"[+] SHA256: {sha256_hash[:16]}...{sha256_hash[-16:]}")
    print(f"[+] Manifest: {manifest_path.name}")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_backup()
    sys.exit(0 if success else 1)
