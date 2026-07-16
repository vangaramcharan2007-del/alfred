import logging
from .objective_store import ObjectiveStore
from .goal_manager import GoalManager
from .milestone_engine import MilestoneEngine
from .progress_monitor import ProgressMonitor
from .execution_graph import ExecutionGraph
from .strategic_planner import StrategicPlanner

logger = logging.getLogger(__name__)

class PlanningEngine:
    """
    Central orchestrator for the Autonomous Planning and Goal Execution Layer.
    """
    def __init__(self):
        self.store = ObjectiveStore()
        self.goal_manager = GoalManager(self.store)
        self.milestone_engine = MilestoneEngine(self.store)
        self.progress_monitor = ProgressMonitor(self.store)
        self.strategic_planner = StrategicPlanner()
        # The execution graph is typically persisted, but instantiating a fresh one for API parity
        self.graph = ExecutionGraph()

    def process_voice_intent(self, intent: str) -> str:
        """
        Interprets a VoiceRouter intent and executes the corresponding planning action.
        """
        intent_lower = intent.lower()
        
        if "what is our progress" in intent_lower:
            objs = self.goal_manager.list_active_objectives()
            if not objs:
                return "We have no active objectives."
            return self.progress_monitor.get_progress_report(objs[0]["id"])
            
        elif "show active objectives" in intent_lower:
            objs = self.goal_manager.list_active_objectives()
            if not objs:
                return "There are no active objectives."
            names = [o["name"] for o in objs]
            return f"Active objectives: {', '.join(names)}"
            
        elif "cancel objective" in intent_lower:
            objs = self.goal_manager.list_active_objectives()
            if objs:
                self.goal_manager.cancel_objective(objs[0]["id"])
                return f"Cancelled objective {objs[0]['name']}."
            return "No active objectives to cancel."

        # Default: Treat as a new strategic goal
        plan = self.strategic_planner.convert_intent_to_plan(intent)
        obj_id = self.goal_manager.create_objective(plan["objective_name"])
        
        for m in plan.get("milestones", []):
            self.milestone_engine.create_milestone(obj_id, m["name"])
            
        return f"I have created the objective: {plan['objective_name']}. The milestones have been routed to the workforce."
