"""Persistent Skill Registry for Phase 92 Autonomous Skill Acquisition."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from jarvisx.skills.models import SkillMetadata, SkillStatus


class PersistentSkillRegistry:
    """Stores versioned, installed skills in var/skills/installed_skills.json."""

    def __init__(self, catalog_path: str = "var/skills/installed_skills.json"):
        self.catalog_path = Path(catalog_path)
        self.catalog: Dict[str, Dict[str, Any]] = {}
        self.load_catalog()

    def load_catalog(self) -> None:
        """Load persistent skill records from disk."""
        if self.catalog_path.exists():
            try:
                self.catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
            except Exception:
                self.catalog = {}
        else:
            self.catalog = {}

    def save_catalog(self) -> None:
        """Persist current catalog to disk."""
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        self.catalog_path.write_text(json.dumps(self.catalog, indent=2), encoding="utf-8")

    def register_installed_skill(self, metadata: SkillMetadata) -> None:
        """Register or update a validated installed skill."""
        if metadata.status in (SkillStatus.DISCOVERED, SkillStatus.GENERATED, SkillStatus.VALIDATED):
            metadata.status = SkillStatus.INSTALLED
        self.catalog[metadata.name] = metadata.to_dict()
        self.save_catalog()

    def get_skill_metadata(self, name: str) -> Optional[SkillMetadata]:
        """Retrieve metadata for a known installed skill."""
        record = self.catalog.get(name)
        if not record:
            return None
        return SkillMetadata(
            name=record["name"],
            version=record.get("version", "1.0.0"),
            description=record.get("description", ""),
            category=record.get("category", "general"),
            inputs=record.get("inputs", []),
            status=SkillStatus(record.get("status", "INSTALLED")),
            created_by=record.get("created_by", "skill_synthesizer"),
            created_at=record.get("created_at", 0.0),
            file_path=record.get("file_path", ""),
            test_path=record.get("test_path", ""),
        )

    def list_installed_skills(self) -> List[Dict[str, Any]]:
        return list(self.catalog.values())
