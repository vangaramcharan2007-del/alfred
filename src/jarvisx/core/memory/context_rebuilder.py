import logging
from .conversation_store import ConversationStore
from .task_memory import TaskMemory

logger = logging.getLogger(__name__)

class ContextRebuilder:
    """
    Reconstructs context after restart. Identifies unfinished work
    and scores recovery confidence.
    """
    def __init__(self, conversation_store: ConversationStore, task_memory: TaskMemory):
        self.conv_store = conversation_store
        self.task_memory = task_memory

    def rebuild_context(self) -> dict:
        """
        Gathers recent state from databases.
        Returns a structured working context and a confidence score.
        """
        active_tasks = self.task_memory.get_active_tasks()
        recent_transcripts = self.conv_store.get_recent_transcripts(limit=10)
        
        # Basic confidence heuristic
        # If we have 1 specific active task, confidence is high.
        # If we have 0 or many, it's lower.
        confidence = 0.5
        primary_task = None
        
        if len(active_tasks) == 1:
            confidence = 0.95
            primary_task = active_tasks[0]
        elif len(active_tasks) > 1:
            confidence = 0.70 # Ambiguous
        else:
            confidence = 0.30 # Nothing clear to resume

        return {
            "recovery_confidence": confidence,
            "active_tasks": active_tasks,
            "recent_transcripts": recent_transcripts,
            "primary_task": primary_task
        }
