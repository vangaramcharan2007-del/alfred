import logging
from .initiative_store import InitiativeStore

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Detects unusual system states like worker silence or execution loops.
    """
    def __init__(self, store: InitiativeStore):
        self.store = store

    def detect_worker_silence(self, worker_id: str, minutes_silent: int):
        if minutes_silent > 15:
            details = {"worker_id": worker_id, "anomaly": "worker_silence", "duration": minutes_silent}
            obs_id = self.store.log_observation("anomaly", details)
            logger.warning(f"Anomaly detected (worker silence): {obs_id}")
            return obs_id
        return None
