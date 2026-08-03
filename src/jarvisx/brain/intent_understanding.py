from __future__ import annotations
from typing import Dict, Any, List, Optional

class IntentUnderstanding:
    INTENT_MAP = {
        "build": "engineering",
        "create": "engineering",
        "develop": "engineering",
        "implement": "engineering",
        "fix": "debugging",
        "debug": "debugging",
        "repair": "debugging",
        "design": "architecture",
        "architect": "architecture",
        "plan": "architecture",
        "review": "review",
        "analyze": "analysis",
        "test": "testing",
        "deploy": "deployment",
        "optimize": "optimization",
        "refactor": "refactoring",
        "evolve": "evolution",
        "improve": "evolution",
        "upgrade": "evolution",
    }

    def analyze_intent(self, user_request: str) -> Dict[str, Any]:
        req_lower = user_request.lower()
        detected_intent = "engineering"
        confidence = 0.80

        for keyword, intent in self.INTENT_MAP.items():
            if keyword in req_lower:
                detected_intent = intent
                confidence = 0.95
                break

        return {
            "raw_request": user_request,
            "intent": detected_intent,
            "confidence": confidence
        }
