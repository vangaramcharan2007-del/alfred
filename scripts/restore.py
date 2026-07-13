import shutil
from pathlib import Path
import sys

def restore_database(backup_file: Path, dest_dir: Path):
    """Restores a SQLite database from a backup."""
    if not backup_file.exists():
        print(f"Error: Backup file {backup_file} not found.")
        sys.exit(1)
        
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract original filename by removing the timestamp (e.g. opdb_20260713_140000.db -> opdb.db)
    # This assumes the original filename did not have underscores before the extension.
    stem = backup_file.stem
    if "_" in stem:
        original_name = stem.rsplit("_", 1)[0] + backup_file.suffix
    else:
        original_name = backup_file.name
        
    dest_file = dest_dir / original_name
    shutil.copy2(backup_file, dest_file)
    print(f"Restored {backup_file.name} to {dest_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python restore.py <backup_file_path>")
        sys.exit(1)
        
    backup_path = Path(sys.argv[1]).resolve()
    base = Path(__file__).resolve().parents[1]
    dest = base / "var"
    restore_database(backup_path, dest)
    print("Restore complete. Please restart Jarvis X services.")
