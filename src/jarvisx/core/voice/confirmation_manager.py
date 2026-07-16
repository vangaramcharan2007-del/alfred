import logging

logger = logging.getLogger(__name__)

class ConfirmationManager:
    """
    Enforces risk-based confirmation policies for sensitive commands.
    """
    def __init__(self):
        self.high_risk_keywords = [
            "delete", "remove", "shutdown", "push production", "deploy production", "drop database"
        ]

    def requires_confirmation(self, command_text: str) -> bool:
        """
        Evaluates whether an explicit voice confirmation is needed.
        """
        text_lower = command_text.lower()
        if any(keyword in text_lower for keyword in self.high_risk_keywords):
            logger.warning(f"High risk action detected requiring confirmation: {command_text}")
            return True
            
        logger.debug("Action deemed low-risk. Execution proceeds.")
        return False
