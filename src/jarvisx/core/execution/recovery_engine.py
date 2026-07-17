"""Recovery Engine — handles retries and objective escalation."""
import time
import logging
from typing import Dict, Any

from jarvisx.core.mission_continuity import MissionContinuityManager

logger = logging.getLogger(__name__)

class RecoveryEngine:
    """Manages failure retries and escalation for TaskExecutor."""
    
    def __init__(self, continuity_manager: MissionContinuityManager, max_retries: int = 3):
        self.continuity = continuity_manager
        self.max_retries = max_retries

    def attempt_recovery(self, step: Dict[str, Any], execute_fn) -> bool:
        """
        Attempt to retry the step.
        Returns True if recovery succeeded, False if escalated to failure.
        """
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Attempt {attempt} failed")
            print(f"Attempt {attempt} failed\nRetrying...")
            
            time.sleep(1.0) # Small delay before retry
            
            # Attempt execution again
            success = execute_fn(step)
            if success:
                logger.info(f"Recovery succeeded on attempt {attempt + 1}")
                return True
                
        # All retries failed
        print(f"Attempt {self.max_retries + 1} failed\nEscalating objective failure.")
        logger.error(f"Escalating objective failure after {self.max_retries} retries.")
        return False
        
    def escalate_failure(self, objective_id: str, title: str, state: Dict[str, Any]) -> None:
        """Persist state to mission continuity."""
        # Continuity manager pulls from the store directly where status is IN_PROGRESS or INTERRUPTED
        pass
