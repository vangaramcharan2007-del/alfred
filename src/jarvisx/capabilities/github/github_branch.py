from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class GitBranch:
    name: str
    commit_sha: str = "head"
    is_remote: bool = False
    is_current: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "commit_sha": self.commit_sha,
            "is_remote": self.is_remote,
            "is_current": self.is_current
        }
