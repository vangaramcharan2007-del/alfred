from __future__ import annotations
from typing import Dict, Any, List, Optional

class ConfidenceEngine:
    """
    Calculates overall execution confidence based on planning score, provider stability, test coverage, and historical success.
    """
    def calculate_confidence(
        self,
        plan_score: float = 0.95,
        provider_stability: float = 0.98,
        test_coverage: float = 0.90,
        historical_success: float = 0.92
    ) -> Dict[str, Any]:
        overall = round(
            (plan_score * 0.25) +
            (provider_stability * 0.25) +
            (test_coverage * 0.25) +
            (historical_success * 0.25),
            2
        )

        return {
            "overall_confidence": overall,
            "confidence_percentage": f"{int(overall * 100)}%",
            "metrics": {
                "planning_confidence": plan_score,
                "provider_confidence": provider_stability,
                "test_confidence": test_coverage,
                "historical_confidence": historical_success
            }
        }
