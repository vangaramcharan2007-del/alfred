"""Data Models for Phase 99: Security & Trust Layer."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PermissionScope(str, Enum):
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE_PROJECT = "filesystem.write(project_only)"
    FILESYSTEM_WRITE_SYSTEM = "filesystem.write(system)"
    TERMINAL_EXECUTE = "terminal.execute"
    NETWORK_ACCESS = "network.access"
    SECRETS_ACCESS = "secrets.access"
    SYSTEM_MUTATION = "system.mutation"


class RiskLevel(str, Enum):
    LOW = "LOW"            # 0 - 29 (Auto-approve)
    MODERATE = "MODERATE"  # 30 - 69 (Logged & sandboxed)
    HIGH = "HIGH"          # 70 - 89 (Approval required)
    CRITICAL = "CRITICAL"  # 90 - 100 (Default Blocked)


@dataclass
class RiskBreakdown:
    base_action_risk: int
    data_sensitivity: int
    privilege_level: int
    blast_radius: int
    irreversibility: int

    @property
    def total_score(self) -> int:
        score = self.base_action_risk + self.data_sensitivity + self.privilege_level + self.blast_radius + self.irreversibility
        return min(100, max(0, score))


@dataclass
class TrustDecision:
    allowed: bool
    risk_score: int
    risk_level: RiskLevel
    reason: str
    required_scope: PermissionScope
    approval_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.value,
            "reason": self.reason,
            "required_scope": self.required_scope.value,
            "approval_required": self.approval_required,
        }


@dataclass
class SecretItem:
    key_name: str
    encrypted_blob_b64: str
    nonce_b64: str
    masked_preview: str
    created_at: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_name": self.key_name,
            "masked_preview": self.masked_preview,
            "created_at": self.created_at,
        }


@dataclass
class AuditEntry:
    id: str
    timestamp: float
    actor: str
    action: str
    risk_score: int
    decision: str  # ALLOWED, BLOCKED, USER_APPROVED
    previous_hash: str
    current_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "risk_score": self.risk_score,
            "decision": self.decision,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
        }
