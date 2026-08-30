"""
Production Safety Layer for Alfred & Friday.
Protects against high-risk and destructive actions by classifying operations
and requiring explicit user authorization.
"""
from __future__ import annotations
import sys
from enum import Enum
from typing import Dict, Any, Optional

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ProductionSafetyGate:
    """Evaluates action safety and prompts for user approval on high-risk actions."""

    @staticmethod
    def classify_risk(command: str, action_type: str = "generic") -> RiskLevel:
        cmd_lower = command.lower()
        if any(kw in cmd_lower for kw in ["rm -rf", "format", "shutdown", "drop database", "delete critical"]):
            return RiskLevel.CRITICAL
        if any(kw in cmd_lower for kw in ["kill", "delete", "rm", "git reset --hard", "overwrite"]):
            return RiskLevel.HIGH
        if any(kw in cmd_lower for kw in ["write", "modify", "update", "create", "mkdir", "compress"]):
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    @classmethod
    def request_approval(
        cls,
        command: str,
        reason: str,
        risk_level: Optional[RiskLevel] = None,
        auto_approve_non_interactive: bool = False,
    ) -> bool:
        if risk_level is None:
            risk_level = cls.classify_risk(command)

        formatted_request = f"""
ACTION REQUEST:
  Command:     {command}
  Reason:      {reason}
  Risk Level:  {risk_level.value}

User approval required:
[Y/N]"""

        print(formatted_request)

        if auto_approve_non_interactive:
            print("[Safety Gate]: Legacy non-interactive auto-approval is disabled.")
        is_tty = bool(sys.stdin and getattr(sys.stdin, "isatty", lambda: False)())
        if not is_tty:
            print("[Safety Gate]: Rejected because explicit approval is unavailable.")
            return False

        try:
            choice = input("Approve action? [Y/n]: ").strip().lower()
            return choice in ("y", "yes", "")
        except EOFError:
            print("[Safety Gate]: Input stream closed. Action rejected.")
            return False
