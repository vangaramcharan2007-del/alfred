import logging
from .conversation_store import ConversationStore
from .task_memory import TaskMemory

logger = logging.getLogger(__name__)

class MemorySummarizer:
    """
    Compresses long histories into concise project states for Long-Term Memory.
    """
    def __init__(self, conv_store: ConversationStore, task_memory: TaskMemory):
        self.conv_store = conv_store
        self.task_memory = task_memory

    def summarize_session(self, session_id: str) -> str:
        """
        Generates a summary of the provided session and stores it.
        """
        completed = self.task_memory.get_completed_tasks_recently(limit=10)
        active = self.task_memory.get_active_tasks()
        
        summary_lines = ["Project Progress:"]
        if completed:
            summary_lines.append("- completed: " + ", ".join([t["task_id"] for t in completed]))
        if active:
            summary_lines.append("- pending: " + ", ".join([t["task_id"] for t in active]))
            
        summary_text = "\n".join(summary_lines)
        self.conv_store.save_summary(session_id, summary_text)
        return summary_text
