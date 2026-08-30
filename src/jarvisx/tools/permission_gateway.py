"""Permission Gateway — bridges Tool Kernel permission levels to existing security infrastructure.

Reuses PermissionEnforcer, TrustEngine, and ProductionSafetyGate.
"""

from __future__ import annotations

import sys
import logging
from typing import Any, Dict, Optional

from jarvisx.tools.tool_kernel import PermissionLevel, ToolSpec

logger = logging.getLogger("jarvisx.permission_gateway")


class PermissionGateway:
    """Maps PermissionLevel to existing security risk scoring and handles user confirmation."""

    def check(
        self,
        tool_spec: ToolSpec,
        arguments: Dict[str, Any],
        interactive: bool = True,
    ) -> Dict[str, Any]:
        """Check if tool execution is permitted.

        Returns:
            {"allowed": bool, "reason": str, "confirmation_text": str | None}
        """
        level = tool_spec.permission_level

        # SAFE — always allowed
        if level == PermissionLevel.SAFE:
            return {"allowed": True, "reason": "SAFE tool auto-approved"}

        # RESTRICTED — always blocked
        if level == PermissionLevel.RESTRICTED:
            return {
                "allowed": False,
                "reason": f"RESTRICTED tool '{tool_spec.name}' is blocked by default security policy.",
            }

        # CONFIRM — requires explicit user confirmation
        if level == PermissionLevel.CONFIRM:
            confirmation_text = self._build_confirmation_text(tool_spec, arguments)

            is_tty = bool(sys.stdin and getattr(sys.stdin, "isatty", lambda: False)())
            if not interactive or not is_tty:
                return {
                    "allowed": False,
                    "reason": "CONFIRM tool denied: non-interactive session cannot provide user approval.",
                    "confirmation_text": confirmation_text,
                }

            # Interactive confirmation
            print(f"\n[TOOL CONFIRM] {confirmation_text}")
            try:
                answer = input("[Y/n] > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                answer = "n"

            if answer in ("y", "yes"):
                logger.info(f"[PermissionGateway] User approved: {tool_spec.name}")
                return {"allowed": True, "reason": "User confirmed"}
            else:
                logger.info(f"[PermissionGateway] User denied: {tool_spec.name}")
                return {"allowed": False, "reason": "User denied confirmation"}

        return {"allowed": False, "reason": f"Unknown permission level: {level}"}

    def _build_confirmation_text(self, tool_spec: ToolSpec, arguments: Dict[str, Any]) -> str:
        """Build human-readable confirmation prompt."""
        parts = [f"Tool '{tool_spec.name}' requires your approval."]
        if arguments:
            safe_args = {k: (v[:80] + "..." if isinstance(v, str) and len(v) > 80 else v) for k, v in arguments.items()}
            parts.append(f"Arguments: {safe_args}")
        parts.append("Do you want to proceed?")
        return " ".join(parts)
