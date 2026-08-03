from __future__ import annotations
from typing import Dict, Any, List, Optional

class DecisionExplainer:
    def explain(self, decision: Dict[str, Any]) -> str:
        lines = [f"Task: {decision.get('task', 'Unknown')}"]
        lines.append(f"Selected Capability: {decision.get('capability', 'N/A')}")
        lines.append(f"Selected Provider: {decision.get('provider', 'N/A')}")
        lines.append(f"Selected Model: {decision.get('model', 'N/A')}")

        reasons = decision.get("reasons", [])
        if reasons:
            lines.append("Reasons:")
            for r in reasons:
                lines.append(f"  - {r}")

        lines.append(f"Risk Level: {decision.get('risk', 'LOW')}")
        lines.append(f"Confidence: {decision.get('confidence', 0.95) * 100}%")
        return "\n".join(lines)
