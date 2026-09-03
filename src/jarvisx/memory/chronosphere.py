import logging
import os
import shutil
import time
import threading
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class BackupHandler(FileSystemEventHandler):
    def __init__(self, backup_dir: Path, source_dir: Path):
        self.backup_dir = backup_dir
        self.source_dir = source_dir
        
    def on_modified(self, event):
        if event.is_directory or ".git" in event.src_path or "__pycache__" in event.src_path:
            return
            
        # Ignore backup dir itself
        if str(self.backup_dir) in event.src_path:
            return

        try:
            # Add small delay to let file write finish
            time.sleep(0.1)
            filepath = Path(event.src_path)
            if not filepath.exists():
                return
                
            rel_path = filepath.relative_to(self.source_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
            
            dest_dir = self.backup_dir / rel_path.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest_path = dest_dir / backup_name
            shutil.copy2(filepath, dest_path)
            
            logger.info(f"[Chronosphere] Backed up {filepath.name}")
        except Exception as e:
            logger.debug(f"[Chronosphere] Backup failed for {event.src_path}: {e}")

class Chronosphere:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.project_dir = Path(__file__).parent.parent.parent.parent.absolute()
        self.backup_dir = self.project_dir / "var" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.observer = None
        self._thread = None

    def start(self):
        """Start the background filesystem observer."""
        if self.observer:
            return
            
        logger.info("[Chronosphere] Initializing real-time file backups...")
        self.observer = Observer()
        handler = BackupHandler(self.backup_dir, self.project_dir)
        self.observer.schedule(handler, str(self.project_dir), recursive=True)
        
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except Exception as e:
            logger.error(f"[Chronosphere] Observer crashed: {e}")
            self.observer.stop()
        self.observer.join()
