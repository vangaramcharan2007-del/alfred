import logging
from .initiative_store import InitiativeStore

logger = logging.getLogger(__name__)

class OpportunityDetector:
    """
    Detects actionable opportunities such as idle workers or outdated dependencies.
    """
    def __init__(self, store: InitiativeStore):
        self.store = store

    def detect_idle_capacity(self, active_tasks: int, total_workers: int):
        if active_tasks < total_workers:
            details = {"idle_workers": total_workers - active_tasks}
            obs_id = self.store.log_observation("opportunity", details)
            logger.info(f"Detected idle capacity opportunity: {obs_id}")
            return obs_id
        return None

    def detect_stalled_objective(self, objective_id: str, days_stalled: int):
        if days_stalled >= 3:
            details = {"objective_id": objective_id, "days_stalled": days_stalled}
            obs_id = self.store.log_observation("opportunity", details)
            logger.info(f"Detected stalled objective: {obs_id}")
            return obs_id
        return None
