import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ObsidianAdapter:
    """
    Direct read/write access to the local Obsidian Vault.
    """
    def __init__(self, vault_path: str = "~/Documents/Obsidian"):
        self.vault_path = Path(vault_path).expanduser()
        if not self.vault_path.exists():
            self.vault_path.mkdir(parents=True, exist_ok=True)
            
    def save_note(self, title: str, content: str):
        filepath = self.vault_path / f"{title}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Saved note to Obsidian: {title}")
            
    def append_note(self, title: str, content: str):
        filepath = self.vault_path / f"{title}.md"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"\n{content}")
            
    def read_note(self, title: str) -> str:
        filepath = self.vault_path / f"{title}.md"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return ""
        
    def list_notes(self) -> list:
        return [f.stem for f in self.vault_path.glob("*.md")]
        
    def search_notes(self, keyword: str) -> list:
        results = []
        for filepath in self.vault_path.glob("*.md"):
            with open(filepath, "r", encoding="utf-8") as f:
                if keyword.lower() in f.read().lower():
                    results.append(filepath.stem)
        return results
        
    def get_backlinks(self, title: str) -> list:
        return self.search_notes(f"[[{title}]]")
