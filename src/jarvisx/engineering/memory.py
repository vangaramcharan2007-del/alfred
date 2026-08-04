from __future__ import annotations

import datetime
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple


@dataclass
class MemoryEntry:
    problem: str
    architecture: str
    chosen_solution: str
    rejected_approaches: List[str] = field(default_factory=list)
    outcome: str = "SUCCESS"
    lessons_learned: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "problem": self.problem,
            "architecture": self.architecture,
            "chosen_solution": self.chosen_solution,
            "rejected_approaches": self.rejected_approaches,
            "outcome": self.outcome,
            "lessons_learned": self.lessons_learned,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryEntry:
        return cls(
            problem=data.get("problem", "Unknown Problem"),
            architecture=data.get("architecture", "Unspecified"),
            chosen_solution=data.get("chosen_solution", "No solution recorded"),
            rejected_approaches=data.get("rejected_approaches", []),
            outcome=data.get("outcome", "UNKNOWN"),
            lessons_learned=data.get("lessons_learned", []),
            timestamp=data.get("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat()),
        )


class EngineeringMemory:
    """
    Offline-first persistent long-term knowledge base that retains solved architectural problems
    and recalls relevant prior engineering interventions for future missions.
    """

    def __init__(self, storage_path: str | Path = "var/db/engineering_memory.jsonl"):
        self.storage_path = Path(storage_path)
        if not self.storage_path.is_absolute():
            # Locate relative to projectroot if possible, or standard var/db
            self.storage_path = (Path.cwd() / self.storage_path).resolve()
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.storage_path.exists():
                self.storage_path.touch()
        except Exception:
            pass

    def save_entry(self, entry: MemoryEntry) -> None:
        self._ensure_storage()
        try:
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
        except Exception as e:
            # Fallback memory buffer without crash if filesystem is read-only
            pass

    def get_all(self) -> List[MemoryEntry]:
        entries: List[MemoryEntry] = []
        if not self.storage_path.exists():
            return entries
        try:
            with open(self.storage_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(MemoryEntry.from_dict(json.loads(line)))
        except Exception:
            pass
        return entries

    def retrieve_similar(self, query: str, max_results: int = 3) -> List[MemoryEntry]:
        query_words = set(re.findall(r"\w+", query.lower()))
        if not query_words:
            return []

        scored: List[Tuple[MemoryEntry, float]] = []
        for entry in self.get_all():
            target_text = f"{entry.problem} {entry.chosen_solution} {entry.architecture} {' '.join(entry.lessons_learned)}".lower()
            target_words = set(re.findall(r"\w+", target_text))
            if not target_words:
                continue
            
            overlap = len(query_words.intersection(target_words))
            score = overlap / len(query_words)
            if overlap > 0:
                scored.append((entry, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in scored[:max_results]]

    def clear_memory(self) -> None:
        if self.storage_path.exists():
            try:
                self.storage_path.write_text("", encoding="utf-8")
            except Exception:
                pass
