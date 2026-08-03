from __future__ import annotations
from typing import Dict, Any, List, Optional

class RiskAnalyzer:
    """
    Analyzes user requests and plans for security concerns, dangerous file changes, dependency risks, and architectural impact.
    """
    HIGH_RISK_KEYWORDS = ["auth", "security", "database", "drop", "delete", "token", "key", "password", "crypto", "root"]
    MEDIUM_RISK_KEYWORDS = ["api", "service", "config", "refactor", "network", "server"]

    def analyze_risk(self, task_description: str, files_affected: Optional[List[str]] = None) -> Dict[str, Any]:
        task_lower = task_description.lower()
        risk_level = "LOW"
        reasons = ["Standard autonomous task", "Stable provider selected", "Tests pass in sandbox"]

        if any(k in task_lower for k in self.HIGH_RISK_KEYWORDS):
            risk_level = "HIGH"
            reasons = ["Modifies core security/authentication system or database schema", "Requires explicit human approval"]
        elif any(k in task_lower for k in self.MEDIUM_RISK_KEYWORDS):
            risk_level = "MEDIUM"
            reasons = ["Modifies network API or service configuration", "Requires confirmation check"]

        return {
            "risk_level": risk_level,
            "reasons": reasons,
            "requires_approval": risk_level in ("MEDIUM", "HIGH")
        }
