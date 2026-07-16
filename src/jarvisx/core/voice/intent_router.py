import logging

logger = logging.getLogger(__name__)

class IntentRouter:
    """
    Analyzes raw transcribed text and categorizes it into a discrete intent.
    Latency target: < 200 ms.
    """
    def __init__(self):
        self.categories = [
            "os_control",        # Open app, close app, shell command
            "development",       # Commit, push, run tests
            "browser",           # Open website, search web
            "interruption",      # Stop, pause, cancel
            "handoff",           # Device transfer
            "planning",          # General goal execution
            "reflection",        # Learning from failures
            "initiative",        # Proactive scanning
            "continuity"         # Resume context
        ]

    def route_intent(self, text: str) -> str:
        """
        In production, uses a small local NLP model (e.g., ONNX model or regex rules)
        to return the category with extremely low latency.
        """
        text_lower = text.lower()
        
        # Interruption
        if text_lower in ["stop", "cancel", "wait", "pause", "nevermind"]:
            return "interruption"
            
        # OS Control
        if any(w in text_lower for w in ["open", "close", "increase brightness", "volume"]):
            return "os_control"
            
        # Development
        if any(w in text_lower for w in ["commit", "push", "run tests", "deploy"]):
            return "development"
            
        # Browser
        if "search" in text_lower or "github.com" in text_lower:
            return "browser"
            
        # Continuity
        if "continue" in text_lower or "resume" in text_lower:
            return "continuity"
            
        # Default fallback to planning/general Jarvis
        return "planning"
