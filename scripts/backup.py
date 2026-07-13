import shutil
import time
from pathlib import Path
import os
import glob

def backup_databases(source_dir: Path, backup_dir: Path, retention_days: int = 30):
    """Backs up SQLite databases and cleans up old backups."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Backup operational db and memory vault databases
    for db_file in source_dir.glob("*.db"):
        dest_file = backup_dir / f"{db_file.stem}_{timestamp}.db"
        shutil.copy2(db_file, dest_file)
        print(f"Backed up {db_file.name} to {dest_file.name}")
        
    # Clean up old backups
    current_time = time.time()
    retention_seconds = retention_days * 86400
    for backup_file in backup_dir.glob("*.db"):
        if current_time - backup_file.stat().st_mtime > retention_seconds:
            os.remove(backup_file)
            print(f"Deleted old backup {backup_file.name}")

if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1]
    source = base / "var"
    backup = base / "var" / "backups"
    backup_databases(source, backup)
    print("Backup complete.")
