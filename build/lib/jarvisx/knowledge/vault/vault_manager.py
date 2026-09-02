"""Obsidian Vault Manager for Jarvis X Knowledge Subsystem."""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from jarvisx.knowledge.models import VaultCategory, KnowledgeSensitivity


class ObsidianVaultManager:
    """Manages Obsidian-compatible folder structures, default templates, and categorizations."""

    DEFAULT_CATEGORIES = [
        (VaultCategory.INBOX, "Raw notes, clippings, quick captures, and unsorted inputs"),
        (VaultCategory.GOALS, "BTech academic goals, career roadmaps, fitness milestones, projects"),
        (VaultCategory.LEARNING, "DSA, System Design, AI/ML, OS, DBMS, Web Development, DevOps"),
        (VaultCategory.PROJECTS, "Jarvis X architecture, specifications, repos, sprint logs"),
        (VaultCategory.REFERENCES, "PDF textbooks, research papers, cheat sheets, documentation links"),
        (VaultCategory.MEMORY, "Personal context, life events, habits, private mental models"),
    ]

    def __init__(self, vault_path: Optional[str] = None):
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            # Default to local var/vault or user home
            self.vault_path = Path("var/vault")
        self.vault_path.mkdir(parents=True, exist_ok=True)

    def initialize_vault(self) -> Dict[str, Any]:
        """Scaffold standard Obsidian Vault directory structure with README index cards."""
        created_dirs = []
        for cat, desc in self.DEFAULT_CATEGORIES:
            folder = self.vault_path / cat.value
            folder.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(folder))

            # Scaffold an index README card if empty
            index_file = folder / "README.md"
            if not index_file.exists():
                content = f"""---
category: {cat.value}
type: index
tags: [vault, index, {cat.value.lower()}]
created: {Path().stat().st_ctime if folder.exists() else 0}
---

# {cat.value}

> {desc}

## Notes in this section
- *Add your markdown notes, research papers, and documents here.*
"""
                index_file.write_text(content, encoding="utf-8")

        return {
            "status": "INITIALIZED",
            "vault_path": str(self.vault_path),
            "folders_created": created_dirs,
        }

    def infer_category_and_sensitivity(self, file_path: Path | str) -> tuple[VaultCategory, KnowledgeSensitivity]:
        """Infer VaultCategory and KnowledgeSensitivity based on relative path within vault."""
        p_str = str(file_path).replace("\\", "/")
        
        if "05_Memory" in p_str or "Memory" in p_str:
            return VaultCategory.MEMORY, KnowledgeSensitivity.SENSITIVE_MEMORY
        elif "01_Goals" in p_str or "Goals" in p_str:
            return VaultCategory.GOALS, KnowledgeSensitivity.PRIVATE_NOTES
        elif "02_Learning" in p_str or "Learning" in p_str or "DSA" in p_str or "DBMS" in p_str:
            return VaultCategory.LEARNING, KnowledgeSensitivity.INTERNAL
        elif "03_Projects" in p_str or "Projects" in p_str:
            return VaultCategory.PROJECTS, KnowledgeSensitivity.INTERNAL
        elif "04_References" in p_str or "References" in p_str:
            return VaultCategory.REFERENCES, KnowledgeSensitivity.PUBLIC
        elif "00_Inbox" in p_str or "Inbox" in p_str:
            return VaultCategory.INBOX, KnowledgeSensitivity.INTERNAL
        else:
            return VaultCategory.GENERAL, KnowledgeSensitivity.INTERNAL

    def list_all_files(self) -> List[Path]:
        """List all supported files in vault."""
        supported_exts = {".md", ".txt", ".pdf", ".json", ".py"}
        found = []
        for root, _, files in os.walk(self.vault_path):
            for f in files:
                p = Path(root) / f
                if p.suffix.lower() in supported_exts:
                    found.append(p)
        return found
