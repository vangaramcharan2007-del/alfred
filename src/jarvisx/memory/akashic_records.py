import logging
import os
import threading
import time
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class AkashicRecords:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.project_dir = Path(__file__).parent.parent.parent.parent.absolute()
        self.docs_dir = self.project_dir / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.index = {}  # Inverted index: word -> set of file paths
        self._thread = None
        self._running = False

    def start(self):
        """Starts the background indexer."""
        if self._running:
            return
            
        logger.info("[Akashic] Starting real-time document indexer...")
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while self._running:
            self._build_index()
            # Re-index every 5 minutes
            time.sleep(300)

    def _build_index(self):
        new_index = {}
        file_count = 0
        
        for root, dirs, files in os.walk(self.project_dir):
            if ".git" in root or "var" in root or "__pycache__" in root:
                continue
                
            for file in files:
                if file.endswith((".md", ".txt", ".json")):
                    filepath = Path(root) / file
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read().lower()
                            words = set(content.split())
                            for word in words:
                                if len(word) > 3:  # skip tiny words
                                    if word not in new_index:
                                        new_index[word] = set()
                                    new_index[word].add(str(filepath))
                        file_count += 1
                    except Exception:
                        pass
        
        self.index = new_index
        logger.info(f"[Akashic] Index built: {file_count} files, {len(self.index)} unique terms.")

    def search(self, query: str) -> list:
        """Search the local document index."""
        query_words = set(query.lower().split())
        results = None
        
        for word in query_words:
            if word in self.index:
                if results is None:
                    results = self.index[word]
                else:
                    results = results.intersection(self.index[word])
                    
        if results:
            return list(results)[:5]
        return []
