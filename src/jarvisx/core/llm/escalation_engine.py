import logging

logger = logging.getLogger(__name__)

class EscalationEngine:
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold

    def requires_escalation(self, confidence: float) -> bool:
        if confidence < self.threshold:
            logger.info(f"Confidence {confidence:.2f} below threshold {self.threshold:.2f}. Escalating to cloud.")
            return True
        return False
