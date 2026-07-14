# src/jarvisx/core/goal_manager.py

class GoalManager:
    """
    Registers goals, prioritizes them, tracks progress, detects stalled goals,
    and supports nested/subgoals for long-running objectives.
    States: PROPOSED, ACTIVE, BLOCKED, COMPLETED, FAILED, ABANDONED
    """
    def __init__(self):
        self.goals = {}

    def register_goal(self, goal_id: str, description: str):
        pass

    def get_goal_status(self, goal_id: str) -> str:
        return "PROPOSED"
