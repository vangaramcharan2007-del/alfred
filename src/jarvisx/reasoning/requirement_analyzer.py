from __future__ import annotations
from typing import Dict, Any, List, Optional

class RequirementAnalyzer:
    """
    Extracts goals, constraints, and missing information from user requests to produce structured requirements.
    """
    def analyze(self, user_request: str) -> Dict[str, Any]:
        req_lower = user_request.lower()

        goals = [user_request]
        constraints = ["Python 3.11+", "Modular Structure", "Automated Pytest Suite"]
        missing_info = []

        is_ambiguous = len(user_request.strip().split()) <= 4 and not any(k in req_lower for k in ["api", "cli", "fix", "bug", "csv", "json", "markdown", "parser", "auth", "password"])
        clarifying_questions = []

        if is_ambiguous:
            clarifying_questions = [
                "What platform or target framework should be used? (e.g., Python CLI, FastAPI REST API)",
                "What core features and inputs are required?",
                "Is persistent database storage required?"
            ]

        if "discord" in req_lower:
            constraints.extend(["Discord API key", "Async event loop"])
            missing_info.append("DISCORD_BOT_TOKEN environment variable")
        elif "weather" in req_lower:
            constraints.extend(["CLI Argument Parsing", "HTTP API Client / Mock Weather Data"])
        elif "rest" in req_lower or "api" in req_lower:
            constraints.extend(["FastAPI / ASGI Framework", "JSON Endpoint Schemas"])
        elif "bug" in req_lower or "fix" in req_lower:
            constraints.extend(["Target Module Identification", "Regression Prevention Test"])
        else:
            constraints.extend(["Dynamic Code Synthesis", "Pytest Suite Generator"])

        return {
            "raw_request": user_request,
            "primary_goal": goals[0],
            "goals": goals,
            "constraints": constraints,
            "missing_info": missing_info,
            "is_ambiguous": is_ambiguous,
            "clarifying_questions": clarifying_questions,
            "complexity": "HIGH" if len(constraints) > 4 else "MEDIUM"
        }

