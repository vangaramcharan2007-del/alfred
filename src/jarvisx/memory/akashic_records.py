"""
Akashic Records — Lightweight on-demand document indexer.
Replaced previous unbounded background time.sleep(300) thread with bounded lazy indexing.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Set

logger = logging.getLogger("jarvisx.akashic_records")


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
        self.index: Dict[str, Set[str]] = {}
        self._indexed = False

    def ensure_indexed(self):
        """Indexes repository on-demand without background loops."""
        if self._indexed:
            return
        logger.info("[Akashic] Performing fast on-demand document indexing...")
        new_index: Dict[str, Set[str]] = {}
        doc_exts = (".md", ".txt", ".json", ".yaml", ".yml")
        for root, dirs, files in os.walk(self.project_dir):
            if any(p in root for p in (".git", "var", "__pycache__", "node_modules")):
                continue
            for file in files:
                if file.endswith(doc_exts):
                    p = Path(root) / file
                    try:
                        with open(p, "r", encoding="utf-8", errors="ignore") as f:
                            words = set(f.read().lower().split())
                            for w in words:
                                if len(w) > 3:
                                    if w not in new_index:
                                        new_index[w] = set()
                                    new_index[w].add(str(p))
                    except Exception:
                        pass
        self.index = new_index
        self._indexed = True
        logger.info(f"[Akashic] Indexed {len(self.index)} terms across documentation.")

    def search(self, query: str) -> List[str]:
        self.ensure_indexed()
        terms = query.lower().split()
        if not terms:
            return []
        matches = set()
        for t in terms:
            if t in self.index:
                matches.update(self.index[t])
        return list(matches)[:15]

    def start(self):
        # Deprecated: No background loop needed
        pass
