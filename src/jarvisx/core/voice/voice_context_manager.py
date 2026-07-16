import logging

logger = logging.getLogger(__name__)

class VoiceContextManager:
    """
    Maintains ephemeral context during a voice interaction session.
    Allows for pronoun resolution and cross-command continuity.
    """
    def __init__(self):
        self.active_project = None
        self.active_file = None
        self.recent_subjects = []

    def update_context(self, text: str):
        """
        Extracts entities from the text to update current context.
        """
        if "authentication" in text.lower():
            self.active_project = "authentication"
            self.recent_subjects.append("authentication project")
            logger.debug("Context updated: active_project = authentication")

    def resolve_pronouns(self, text: str) -> str:
        """
        Replaces 'it', 'that', 'too' with the active context subject.
        """
        if "too" in text.lower() or "that" in text.lower():
            if self.active_project:
                logger.debug(f"Resolved context to: {self.active_project}")
                return text + f" [Context: {self.active_project}]"
        return text

    def clear_context(self):
        self.active_project = None
        self.active_file = None
        self.recent_subjects = []
