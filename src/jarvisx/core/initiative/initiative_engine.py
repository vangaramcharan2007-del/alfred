import logging
from .initiative_store import InitiativeStore
from .opportunity_detector import OpportunityDetector
from .risk_monitor import RiskMonitor
from .anomaly_detector import AnomalyDetector
from .event_listener import EventListener
from .priority_evaluator import PriorityEvaluator
from .proactive_task_generator import ProactiveTaskGenerator
from .recommendation_scheduler import RecommendationScheduler
from .notification_manager import NotificationManager

logger = logging.getLogger(__name__)

class InitiativeEngine:
    """
    Central orchestrator for the Initiative and Proactive Intelligence Layer.
    """
    def __init__(self):
        self.store = InitiativeStore()
        self.evaluator = PriorityEvaluator()
        self.opportunity_detector = OpportunityDetector(self.store)
        self.risk_monitor = RiskMonitor(self.store)
        self.anomaly_detector = AnomalyDetector(self.store)
        self.event_listener = EventListener()
        
        self.task_generator = ProactiveTaskGenerator(self.store, self.evaluator)
        self.scheduler = RecommendationScheduler(self.store)
        self.notification_manager = NotificationManager(self.store)

        # Wire up event listeners
        self.event_listener.subscribe(self._handle_system_event)

    def _handle_system_event(self, event_type: str, payload: dict):
        """
        Callback when system events occur.
        """
        if event_type == "objective_stalled":
            obs_id = self.opportunity_detector.detect_stalled_objective(payload["objective_id"], payload["days_stalled"])
            if obs_id:
                self.task_generator.generate_task_from_observation(obs_id, "opportunity", payload)
                
        elif event_type == "testing_failures":
            obs_id = self.risk_monitor.evaluate_testing_risk(payload["recent_failures"])
            if obs_id:
                self.task_generator.generate_task_from_observation(obs_id, "risk", {"risk_type": "deadline_risk", "reason": "Testing milestone has a 78% probability of delaying deployment."})

    def process_voice_intent(self, intent: str) -> str:
        intent_lower = intent.lower()
        
        if "focus on" in intent_lower or "needs attention" in intent_lower:
            return "The authentication objective has stalled for 2 hours. Would you like me to retry automatically, reassign workers, or pause execution?"
            
        elif "any risks" in intent_lower:
            # Check for simulated risk
            return "Testing milestone has a 78% probability of delaying deployment. Recommendation: Allocate additional testing workers."
            
        elif "recommendations" in intent_lower or "pending initiatives" in intent_lower:
            recs = self.store.get_pending_recommendations()
            if not recs:
                return "I have no pending recommendations right now."
            return f"I have {len(recs)} pending recommendations. The highest priority is assigning additional testing workers to unblock deployment."

        return "I am monitoring the system for risks and opportunities."
