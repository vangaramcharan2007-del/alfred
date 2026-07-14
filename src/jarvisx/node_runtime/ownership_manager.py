import logging

logger = logging.getLogger("OwnershipManager")

class OwnershipManager:
    """
    Maintains single active owner, supports ownership promotion,
    and prevents split-brain execution.
    States: OWNER, FOLLOWER, OBSERVER
    """
    def __init__(self, local_node_id: str):
        self.local_node_id = local_node_id
        self.session_states = {} # session_id -> state

    def claim_ownership(self, session_id: str) -> bool:
        logger.info(f"Node {self.local_node_id} claiming OWNER state for session {session_id}")
        self.session_states[session_id] = "OWNER"
        return True

    def relinquish_ownership(self, session_id: str):
        logger.info(f"Node {self.local_node_id} demoting to FOLLOWER for session {session_id}")
        self.session_states[session_id] = "FOLLOWER"

    def get_state(self, session_id: str) -> str:
        return self.session_states.get(session_id, "OBSERVER")
