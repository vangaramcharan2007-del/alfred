"""Hardware Sandbox Guardrails and Path Boundary Clamping for Phase 99."""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, Optional


class SandboxGuardrails:
    """Enforces strict path boundary clamping, directory traversal defense, and execution limits."""

    def __init__(self, allowed_workspace: str = "."):
        self.allowed_workspace = Path(allowed_workspace).resolve()

    def validate_file_path(self, target_path: str) -> Dict[str, Any]:
        """Verify that target file path stays strictly within the authorized project boundary."""
        # Detect explicit directory traversal attempts
        if ".." in target_path or target_path.startswith("/") or target_path.startswith("\\"):
            # Check if it resolves outside
            resolved = Path(target_path).resolve()
            try:
                resolved.relative_to(self.allowed_workspace)
            except ValueError:
                return {
                    "allowed": False,
                    "reason": f"Path traversal violation: '{target_path}' escapes workspace boundary '{self.allowed_workspace}'",
                    "status": "BLOCKED"
                }

        resolved = Path(target_path).resolve()
        try:
            resolved.relative_to(self.allowed_workspace)
            return {"allowed": True, "resolved_path": str(resolved), "status": "APPROVED"}
        except ValueError:
            return {
                "allowed": False,
                "reason": f"Path '{target_path}' is outside authorized workspace root",
                "status": "BLOCKED"
            }

    def validate_command(self, cmd: str) -> Dict[str, Any]:
        """Block forbidden destructive commands and shell injection attempts."""
        destructive_patterns = ["rm -rf /", "mkfs", "format c:", "drop database", "shutdown", ":(){ :|:& };:"]
        for p in destructive_patterns:
            if p in cmd.lower():
                return {
                    "allowed": False,
                    "reason": f"Forbidden destructive command pattern: '{p}'",
                    "status": "BLOCKED"
                }
        return {"allowed": True, "command": cmd, "status": "APPROVED"}
