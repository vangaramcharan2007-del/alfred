"""Adaptive Goal Decomposition Planner for Jarvis X (Layer 2 - Planning).

Deconstructs high-level goals into structured Mission Trees with dependencies,
estimated effort, priority, and completion criteria.
"""

import uuid
from typing import Any, Dict, List, Optional

from jarvisx.goals import GoalTracker
from jarvisx.missions.mission import Mission


class AdaptivePlanner:
    """Zero-fluff production goal decomposition and mission tree planner."""

    def __init__(self, goal_tracker: Optional[GoalTracker] = None):
        self.goal_tracker = goal_tracker or GoalTracker()

    def decompose_goal_into_mission_tree(self, goal_text: str, goal_type: str = "LONG_TERM") -> Dict[str, Any]:
        """Deconstruct high-level goal into a hierarchical mission tree."""
        goal_clean = goal_text.strip()
        g_lower = goal_clean.lower()

        # Seed standard decomposition templates based on goal domain
        subtasks = []
        if "machine learning" in g_lower or "ml" in g_lower or "ai" in g_lower:
            subtasks = [
                {"title": "Complete Python & NumPy Revision", "estimated_effort": "2 hours", "priority": "HIGH", "criteria": "Pass Python AST check and vector math quiz", "deps": []},
                {"title": "Learn ML Mathematics & Linear Algebra", "estimated_effort": "3 hours", "priority": "HIGH", "criteria": "Synthesize notes on matrix transformations", "deps": ["Complete Python & NumPy Revision"]},
                {"title": "Learn Core ML Algorithms & Scikit-Learn", "estimated_effort": "4 hours", "priority": "MEDIUM", "criteria": "Train classification and regression baselines", "deps": ["Learn ML Mathematics & Linear Algebra"]},
                {"title": "Build First End-to-End ML Model", "estimated_effort": "5 hours", "priority": "HIGH", "criteria": "Validate accuracy >= 85% on benchmark dataset", "deps": ["Learn Core ML Algorithms & Scikit-Learn"]},
                {"title": "Deploy Model Project to Production", "estimated_effort": "3 hours", "priority": "MEDIUM", "criteria": "Deploy inference pipeline with clean tests", "deps": ["Build First End-to-End ML Model"]},
            ]
        elif "calculus" in g_lower or "math" in g_lower or "dsa" in g_lower:
            subtasks = [
                {"title": "Review Core Theorem Foundations", "estimated_effort": "1 hour", "priority": "HIGH", "criteria": "Complete chapter concept summary", "deps": []},
                {"title": "Solve Practice Problem Set 1", "estimated_effort": "2 hours", "priority": "HIGH", "criteria": "Score >= 90% on practice problems", "deps": ["Review Core Theorem Foundations"]},
                {"title": "Synthesize Flashcards & Mock Exam", "estimated_effort": "1.5 hours", "priority": "MEDIUM", "criteria": "Generate 20 SQLite flashcards", "deps": ["Solve Practice Problem Set 1"]},
            ]
        else:
            subtasks = [
                {"title": f"Phase 1: Research & Discovery for {goal_clean}", "estimated_effort": "1 hour", "priority": "HIGH", "criteria": "Synthesize initial roadmap digest", "deps": []},
                {"title": f"Phase 2: Core Execution for {goal_clean}", "estimated_effort": "3 hours", "priority": "HIGH", "criteria": "Complete primary deliverables", "deps": [f"Phase 1: Research & Discovery for {goal_clean}"]},
                {"title": f"Phase 3: Validation & Optimization for {goal_clean}", "estimated_effort": "2 hours", "priority": "MEDIUM", "criteria": "Verify 100% completion without regressions", "deps": [f"Phase 2: Core Execution for {goal_clean}"]},
            ]

        # Register top-level goal in GoalTracker
        parent_goal = self.goal_tracker.add_goal(
            goal=goal_clean,
            goal_type=goal_type,
            next_action=subtasks[0]["title"],
            confidence=0.95,
        )

        mission_tree = []
        for idx, st in enumerate(subtasks):
            m = Mission(
                title=st["title"],
                user_request=st["title"],
                intent="adaptive_planning",
                capability="adaptive_planner",
                status="PENDING",
                context={
                    "parent_goal_id": parent_goal["goal_id"],
                    "estimated_effort": st["estimated_effort"],
                    "priority": st["priority"],
                    "completion_criteria": st["criteria"],
                    "dependencies": st["deps"],
                    "tree_index": idx + 1,
                },
            )
            mission_tree.append(m)

        return {
            "status": "completed",
            "goal_id": parent_goal["goal_id"],
            "goal": goal_clean,
            "missions_count": len(mission_tree),
            "mission_tree": [m.to_dict() for m in mission_tree],
        }
