"""
Omniscient Indexer — Infinite Data Ingestion.
Recursively scans the local filesystem, chunks documents/code, and embeds them into Vector Memory.
"""
import os
import time
import logging
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class OmniIndexer:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.target_dirs = [os.path.expanduser("~/Documents")]
        self.extensions = {".txt", ".md", ".py", ".json", ".csv"}

    def _crawl(self):
        """Background crawler that embeds files into Vector RAG."""
        try:
            from jarvisx.memory.vector_memory import VectorMemory
            vm = VectorMemory("omniscient_drive")
        except ImportError:
            return

        logger.info("[OmniIndexer] Starting background indexing...")
        files_indexed = 0
        
        for d in self.target_dirs:
            if not os.path.exists(d): continue
            for root, _, files in os.walk(d):
                if not self._running: return
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.extensions:
                        path = os.path.join(root, file)
                        try:
                            # Skip large files > 1MB
                            if os.path.getsize(path) > 1024 * 1024: continue
                            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(4000) # Read first chunk
                                if content.strip():
                                    vm.add_memory(content, {"source": path})
                                    files_indexed += 1
                        except Exception:
                            pass
                time.sleep(0.5) # Throttle to prevent CPU spike
                
        logger.info(f"[OmniIndexer] Indexing complete. Indexed {files_indexed} files.")

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._crawl, daemon=True)
        self._thread.start()
        
    def stop(self):
        self._running = False
