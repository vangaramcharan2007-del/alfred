import time
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class WhatsAppListener:
    """Listens for new WhatsApp messages (files)."""
    
    def __init__(self, download_dir: str):
        self.download_dir = download_dir
        self._last_mtime = 0
        self._initialize_mtime()
        
    def _initialize_mtime(self):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)
            return
            
        mtimes = [os.path.getmtime(os.path.join(self.download_dir, f)) 
                  for f in os.listdir(self.download_dir) 
                  if os.path.isfile(os.path.join(self.download_dir, f))]
        if mtimes:
            self._last_mtime = max(mtimes)

    def check_for_new_file(self) -> Optional[str]:
        """
        Polls the download directory for a new file.
        In a real desktop automation scenario, this could also monitor OCR regions 
        or UI Automation events for incoming messages. 
        For maximum reliability, monitoring the Downloads folder is a robust fallback.
        """
        if not os.path.exists(self.download_dir):
            return None
            
        newest_file = None
        newest_mtime = self._last_mtime
        
        for f in os.listdir(self.download_dir):
            filepath = os.path.join(self.download_dir, f)
            if not os.path.isfile(filepath):
                continue
                
            # Only care about Word documents
            if not f.endswith(".docx"):
                continue
                
            mtime = os.path.getmtime(filepath)
            if mtime > newest_mtime:
                newest_mtime = mtime
                newest_file = filepath
                
        if newest_file:
            self._last_mtime = newest_mtime
            return newest_file
            
        return None
