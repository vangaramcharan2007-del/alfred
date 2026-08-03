from __future__ import annotations
from typing import Dict, Any, List, Optional

class DecisionExplainer:
    def explain(self, decision: Dict[str, Any]) -> str:
        task = decision.get("task", "Unknown")
        cap = decision.get("capability", "N/A")
        prov = decision.get("provider", "N/A")
        model = decision.get("model", "N/A")
        reasons = decision.get("reasons", [])
        risk = decision.get("risk", "Low")

        lines = [
            f"Task:",
            f"{task}",
            "",
            f"Decision:",
            "",
            f"Capability:",
            f"{cap}",
            "",
            f"Provider:",
            f"{prov}",
            "",
            f"Model:",
            f"{model}",
            "",
            f"Reason:"
        ]
        for r in reasons:
            lines.append(f"{r}")

        lines.extend([
            "",
            f"Risk:",
            f"{risk}"
        ])
        return "\n".join(lines)

