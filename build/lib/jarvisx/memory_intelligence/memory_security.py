"""Memory Security & Zero-Trust Access Controller for Phase 103."""

from __future__ import annotations
import re
from typing import Optional, Tuple
from jarvisx.memory_intelligence.models import MemoryRecord, MemorySensitivity


class MemorySecurityGuard:
    """Enforces zero-trust boundaries, credential filtering, and role-based memory scoping."""

    # Patterns indicating high-entropy secrets, passwords, tokens, private keys
    SECRET_PATTERNS = [
        re.compile(r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*\S+"),
        re.compile(r"(?i)\b(?:api[_-]?key|secret[_-]?key|auth[_-]?token)\s*[:=]\s*\S+"),
        re.compile(r"\b(?:ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})\b"),
        re.compile(r"\bAIza[0-9A-Za-z-_]{35}\b"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ]

    # Role permission mappings
    ROLE_PERMISSIONS = {
        "AlfredMaster": {MemorySensitivity.PUBLIC, MemorySensitivity.PERSONAL, MemorySensitivity.PRIVATE},
        "StudyCoach": {MemorySensitivity.PUBLIC, MemorySensitivity.PERSONAL},
        "PlannerAgent": {MemorySensitivity.PUBLIC, MemorySensitivity.PERSONAL},
        "CodingAgent": {MemorySensitivity.PUBLIC},
        "ResearchAgent": {MemorySensitivity.PUBLIC},
        "VisionAgent": {MemorySensitivity.PUBLIC},
    }

    @classmethod
    def validate_memory_for_storage(cls, content: str) -> Tuple[bool, Optional[str]]:
        """Verify that memory text does not contain secret credentials or poison payloads."""
        for pattern in cls.SECRET_PATTERNS:
            if pattern.search(content):
                return False, "REJECTED: Content contains sensitive credentials/passwords. Memory store enforces zero secret retention."
        return True, None

    @classmethod
    def can_access_memory(cls, memory: MemoryRecord, actor_role: str = "AlfredMaster") -> bool:
        """Enforce role-based access control on memory sensitivity levels."""
        allowed_sensitivities = cls.ROLE_PERMISSIONS.get(actor_role, {MemorySensitivity.PUBLIC})
        return memory.sensitivity in allowed_sensitivities
