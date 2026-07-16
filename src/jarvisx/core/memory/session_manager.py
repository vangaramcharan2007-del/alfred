import uuid
import time
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages active session lifecycle.
    Persists session IDs across restarts using simple file tracking.
    """
    def __init__(self, session_file="var/current_session.txt"):
        self.session_file = session_file
        self.current_session_id = None
        self._init_session()

    def _init_session(self):
        # Always generate a new session ID for this boot
        self.current_session_id = str(uuid.uuid4())
        
        # Check for abnormal shutdown (did previous session finish cleanly?)
        # For MVP, we simply overwrite, but this can track clean exits.
        try:
            with open(self.session_file, "w") as f:
                f.write(self.current_session_id)
            logger.info(f"Started new session: {self.current_session_id}")
        except Exception as e:
            logger.error(f"Failed to write session file: {e}")

    def get_session_id(self) -> str:
        return self.current_session_id

    def mark_clean_shutdown(self):
        # In a full implementation, we'd delete the file or mark it clean.
        pass
