import logging
from typing import Dict, Any

class ConflictResolver:
    """
    Arbitrates state conflicts between devices and cloud workers.
    Priority: Manual User Edit > Active Device State > Cloud Worker State > Historical State
    """
    
    def resolve_state(self, local_state: Dict[str, Any], incoming_state: Dict[str, Any]) -> Dict[str, Any]:
        logging.info("[ConflictResolver] Evaluating state conflict...")
        # Simplistic priority arbitration mock
        local_priority = self._get_priority(local_state.get('source', 'historical'))
        incoming_priority = self._get_priority(incoming_state.get('source', 'historical'))
        
        if incoming_priority > local_priority:
            logging.info(f"[ConflictResolver] Accepted incoming state from {incoming_state.get('source')} over local {local_state.get('source')}.")
            return incoming_state
        else:
            logging.info(f"[ConflictResolver] Retained local state ({local_state.get('source')}) over incoming {incoming_state.get('source')}.")
            return local_state
            
    def _get_priority(self, source: str) -> int:
        priorities = {
            'user': 4,
            'active_device': 3,
            'cloud_worker': 2,
            'historical': 1
        }
        return priorities.get(source, 1)
