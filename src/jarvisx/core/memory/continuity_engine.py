import logging
from .context_rebuilder import ContextRebuilder

logger = logging.getLogger(__name__)

class ContinuityEngine:
    """
    Parses resume intents and responds with the recovered context state.
    """
    def __init__(self, rebuilder: ContextRebuilder):
        self.rebuilder = rebuilder

    def is_resume_intent(self, text: str) -> bool:
        lower = text.lower()
        resume_keywords = ["continue", "resume", "what were we doing", "yesterday's work", "previous task"]
        return any(kw in lower for kw in resume_keywords)

    def process_resume(self) -> str:
        context = self.rebuilder.rebuild_context()
        confidence = context.get("recovery_confidence", 0.0)
        active_tasks = context.get("active_tasks", [])

        if confidence < 0.5 or not active_tasks:
            return "I found multiple unfinished projects, or none at all. Did you mean authentication or workforce integration?"

        # We have high confidence and active tasks
        task_names = [t["task_id"] for t in active_tasks]
        
        response = "We were working on your previous tasks. "
        response += "The following tasks are pending: " + ", ".join(task_names) + ". "
        response += "Would you like me to continue?"

        return response
