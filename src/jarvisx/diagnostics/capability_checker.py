from __future__ import annotations
from typing import Dict, Any, Optional
from jarvisx.diagnostics.dependency_checker import DependencyChecker
from jarvisx.diagnostics.integration_checker import IntegrationChecker

class CapabilityChecker:
    """
    Aggregates dependency checks and live integration checks to report true system status.
    """
    def __init__(
        self,
        dep_checker: Optional[DependencyChecker] = None,
        int_checker: Optional[IntegrationChecker] = None
    ):
        self.dep_checker = dep_checker or DependencyChecker()
        self.int_checker = int_checker or IntegrationChecker()

    def get_system_capabilities(self) -> Dict[str, Any]:
        deps = self.dep_checker.run_full_check()
        integrations = self.int_checker.run_integration_checks()

        online_count = sum(1 for status in integrations.values() if status == "ONLINE")

        return {
            "integrations": integrations,
            "dependencies": deps,
            "online_subsystems": online_count,
            "total_subsystems": len(integrations),
            "system_health": "HEALTHY" if online_count >= 4 else "DEGRADED"
        }
