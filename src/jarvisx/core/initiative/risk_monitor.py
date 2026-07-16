import logging
from .initiative_store import InitiativeStore

logger = logging.getLogger(__name__)

class RiskMonitor:
    """
    Monitors deadlines, dependencies, and worker failures to anticipate risks.
    """
    def __init__(self, store: InitiativeStore):
        self.store = store

    def evaluate_testing_risk(self, recent_failures: int):
        """
        Example heuristic: If tests fail multiple times, it risks deployment.
        """
        if recent_failures > 3:
            details = {
                "risk_type": "deadline_risk",
                "probability": 0.78,
                "reason": "Testing milestone has a 78% probability of delaying deployment due to recent failures."
            }
            obs_id = self.store.log_observation("risk", details)
            logger.warning(f"High risk detected: {obs_id}")
            return obs_id
        return None
