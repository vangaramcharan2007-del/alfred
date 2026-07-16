import logging
import uuid
from .initiative_store import InitiativeStore

logger = logging.getLogger(__name__)

class RecommendationScheduler:
    """
    Schedules autonomous actions based on approval policies.
    """
    def __init__(self, store: InitiativeStore):
        self.store = store

    def schedule_action(self, recommendation_id: str, payload: str, policy: str):
        """
        Policies: always_ask, ask_for_high_risk, fully_autonomous
        """
        if policy == "fully_autonomous":
            status = "ready_to_execute"
        else:
            status = "requires_approval"
            
        self.store.conn.execute(
            "INSERT INTO scheduled_actions (id, recommendation_id, action_payload, status) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), recommendation_id, payload, status)
        )
        self.store.conn.commit()
