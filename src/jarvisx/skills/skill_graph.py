"""Skill Dependency Graph for Phase 92.5 Capability Intelligence Layer."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List, Set


class SkillDependencyGraph:
    """Manages directed dependency relationships between capabilities."""

    def __init__(self, graph_file: str = "var/skills/skill_dependencies.json"):
        self.graph_file = Path(graph_file)
        self.dependencies: Dict[str, List[str]] = {}
        self.load_graph()

    def load_graph(self) -> None:
        if self.graph_file.exists():
            try:
                self.dependencies = json.loads(self.graph_file.read_text(encoding="utf-8"))
            except Exception:
                self.dependencies = {}
        else:
            self.dependencies = {
                "ocr_flashcard_skill": ["image_to_text", "document_generator"],
                "study_planner_skill": ["document_generator", "quiz_generator"],
                "code_refactor_skill": ["file_generator", "system_cleaner"]
            }

    def save_graph(self) -> None:
        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        self.graph_file.write_text(json.dumps(self.dependencies, indent=2), encoding="utf-8")

    def register_dependency(self, skill_name: str, depends_on: List[str]) -> None:
        self.dependencies[skill_name] = depends_on
        self.save_graph()

    def get_dependencies(self, skill_name: str) -> List[str]:
        return self.dependencies.get(skill_name, [])

    def get_affected_dependents(self, broken_or_retired_skill: str) -> List[str]:
        """Find all higher-level skills affected if a base capability is disabled or retired."""
        affected = []
        for parent_skill, deps in self.dependencies.items():
            if broken_or_retired_skill in deps:
                affected.append(parent_skill)
        return affected
