import logging
import threading
import time

from jarvisx.automation.real_system_cleaner import RealSystemCleaner

logger = logging.getLogger(__name__)

class SystemCleanerDaemon:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self._running = False
        self._thread = None
        self.cleaner = RealSystemCleaner()
        
    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="SystemCleaner")
        self._thread.start()
        logger.info("[SystemCleaner] Daemon online. Sweeping disk space every 6 hours.")
        
    def _loop(self):
        while self._running:
            try:
                # Delay first run so it doesn't freeze the boot sequence
                time.sleep(60)
                res = self.cleaner.scan_and_clean_temp_bloat(delete=True)
                if res["files_deleted"] > 0 or res["dirs_deleted"] > 0:
                    mb = res["bytes_reclaimed"] / (1024 * 1024)
                    logger.info(f"[SystemCleaner] Auto-purge complete. Deleted {res['files_deleted']} files. Reclaimed {mb:.2f} MB.")
            except Exception as e:
                logger.error(f"[SystemCleaner] Failed to run cleaner: {e}")
            # Sleep 6 hours
            time.sleep(21600)
