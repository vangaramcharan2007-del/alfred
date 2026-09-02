"""Data Models and Lifecycle States for Phase 92 Autonomous Skill Acquisition."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class SkillStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    GENERATED = "GENERATED"
    TESTING = "TESTING"
    VALIDATED = "VALIDATED"
    INSTALLED = "INSTALLED"
    DISABLED = "DISABLED"
    REJECTED = "REJECTED"


@dataclass
class CapabilityGap:
    """Represents a missing capability gap identified from a goal."""
    required_capability: str
    reason: str
    confidence: float = 0.9
    suggested_inputs: List[str] = field(default_factory=list)
    suggested_category: str = "general"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "required_capability": self.required_capability,
            "reason": self.reason,
            "confidence": self.confidence,
            "suggested_inputs": self.suggested_inputs,
            "suggested_category": self.suggested_category,
        }


@dataclass
class SandboxPolicy:
    """Resource, security, and filesystem limits for testing untrusted synthesized skills."""
    max_runtime_seconds: float = 30.0
    max_memory_mb: int = 512
    network_access: bool = False
    filesystem_scope: str = "sandbox/"
    allow_privileged_escalation: bool = False


@dataclass
class SkillMetadata:
    """Versioned metadata record for an installed or validated skill."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    category: str = "general"
    inputs: List[str] = field(default_factory=list)
    status: SkillStatus = SkillStatus.DISCOVERED
    created_by: str = "skill_synthesizer"
    created_at: float = 0.0
    file_path: str = ""
    test_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "inputs": self.inputs,
            "status": self.status.value if isinstance(self.status, SkillStatus) else self.status,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "file_path": self.file_path,
            "test_path": self.test_path,
        }


@dataclass
class SkillValidationResult:
    """Outcome of sandbox execution and policy validation."""
    passed: bool
    status: SkillStatus
    execution_time_sec: float
    output: Any = None
    error: Optional[str] = None
    policy_violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "status": self.status.value if isinstance(self.status, SkillStatus) else self.status,
            "execution_time_sec": self.execution_time_sec,
            "output": self.output,
            "error": self.error,
            "policy_violations": self.policy_violations,
        }
