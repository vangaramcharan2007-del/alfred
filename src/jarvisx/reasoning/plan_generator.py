from __future__ import annotations
import uuid
import time
from typing import Dict, Any, List, Optional
from jarvisx.reasoning.requirement_analyzer import RequirementAnalyzer
from jarvisx.reasoning.task_reasoner import TaskReasoner

class PlanGenerator:
    """
    Generates dynamic execution plans with tool, model, and capability selections.
    """
    def __init__(
        self,
        analyzer: Optional[RequirementAnalyzer] = None,
        reasoner: Optional[TaskReasoner] = None
    ):
        self.analyzer = analyzer or RequirementAnalyzer()
        self.reasoner = reasoner or TaskReasoner()

    def generate_plan(self, user_request: str) -> Dict[str, Any]:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        reqs = self.analyzer.analyze(user_request)
        tasks = self.reasoner.decompose(reqs)

        raw = user_request.lower()
        if "discord" in raw:
            model = "qwen2.5-coder:7b"
            capabilities = ["Coding Agent", "Repository Analyzer", "Test Runner"]
        elif "weather" in raw:
            model = "qwen2.5-coder:7b"
            capabilities = ["Coding Agent", "Test Runner", "Git Service"]
        else:
            model = "qwen2.5-coder:7b"
            capabilities = ["Architecture Agent", "Coding Agent", "Test Runner", "Git Service"]

        return {
            "plan_id": plan_id,
            "user_request": user_request,
            "requirements": reqs,
            "tasks": tasks,
            "selected_model": model,
            "selected_capabilities": capabilities,
            "created_at": time.time()
        }
