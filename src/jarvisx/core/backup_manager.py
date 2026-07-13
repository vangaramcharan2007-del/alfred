import os
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """Handles archival, compression, and retention of system states."""
    
    def __init__(self, data_dir: Path, backup_dir: Path):
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.retention_daily = 7
        self.retention_weekly = 8
        self.retention_monthly = 12
        
    def create_backup(self, tag: str = "daily") -> Path:
        """Creates a tar.gz archive of the var directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"jarvisx_{tag}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            logger.info(f"Starting backup: {backup_name}")
            archive_path = shutil.make_archive(
                str(backup_path),
                'gztar',
                root_dir=str(self.data_dir.parent),
                base_dir=self.data_dir.name
            )
            logger.info(f"Backup created: {archive_path}")
            return Path(archive_path)
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
            
    def enforce_retention(self) -> None:
        """Enforces the 7/8/12 retention policy on existing backups."""
        backups = list(self.backup_dir.glob("jarvisx_*.tar.gz"))
        
        dailies = sorted([b for b in backups if "_daily_" in b.name], key=lambda x: x.stat().st_mtime, reverse=True)
        weeklies = sorted([b for b in backups if "_weekly_" in b.name], key=lambda x: x.stat().st_mtime, reverse=True)
        monthlies = sorted([b for b in backups if "_monthly_" in b.name], key=lambda x: x.stat().st_mtime, reverse=True)
        
        def prune(archives: list[Path], keep: int):
            for arch in archives[keep:]:
                try:
                    arch.unlink()
                    logger.info(f"Pruned old backup: {arch.name}")
                except Exception as e:
                    logger.error(f"Failed to prune {arch.name}: {e}")
                    
        prune(dailies, self.retention_daily)
        prune(weeklies, self.retention_weekly)
        prune(monthlies, self.retention_monthly)

    def run_scheduled_backup(self) -> None:
        """Executes a daily backup and handles weekly/monthly promotions."""
        now = datetime.now()
        
        # Always create a daily backup
        self.create_backup("daily")
        
        # If it's Sunday, create a weekly backup
        if now.weekday() == 6:
            self.create_backup("weekly")
            
        # If it's the 1st of the month, create a monthly backup
        if now.day == 1:
            self.create_backup("monthly")
            
        self.enforce_retention()
