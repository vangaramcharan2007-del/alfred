from __future__ import annotations
from typing import Dict, Any, Optional
from jarvisx.diagnostics.capability_checker import CapabilityChecker

class SystemHealthReporter:
    """
    Generates honest startup report showing true ONLINE / OFFLINE statuses without fake states.
    """
    def __init__(self, checker: Optional[CapabilityChecker] = None):
        self.checker = checker or CapabilityChecker()

    def generate_startup_banner(self) -> str:
        caps = self.checker.get_system_capabilities()
        integrations = caps["integrations"]

        lines = [
            "=========================",
            "       JARVIS X",
            "=========================",
            ""
        ]

        for srv in ["Memory", "LLM", "Voice", "Vision", "Git", "Agents"]:
            status = integrations.get(srv, "OFFLINE")
            lines.append(f"{srv:<12} ........ {status}")

        lines.extend([
            "",
            "Alfred online.",
            ""
        ])

        return "\n".join(lines)
