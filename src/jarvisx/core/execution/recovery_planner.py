"""Recovery Planner — implements a strategy pattern for objective recovery."""
import os
import logging
from typing import Dict, Any, List, Optional, Callable

from jarvisx.core.execution.reflection_engine import ReflectionResult
from jarvisx.core.execution.capability_registry import CapabilityRegistry
from jarvisx.core.execution.failure_classifier import FailureCategory

logger = logging.getLogger(__name__)

class RecoveryStrategy:
    """Base class for all recovery strategies."""
    def can_handle(self, result: ReflectionResult, step: Dict[str, Any]) -> bool:
        return False
        
    def recover(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Attempt recovery. Return True if successful."""
        return False


class RetryStrategy(RecoveryStrategy):
    """Simple retry for transient failures."""
    
    def can_handle(self, result: ReflectionResult, step: Dict[str, Any]) -> bool:
        return result.recommendation == "retry"
        
    def recover(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        executor_fn = context.get("executor_fn")
        max_retries = context.get("max_retries", 3)
        current_retry = context.get("current_retry", 0)
        
        if current_retry < max_retries:
            logger.info(f"Retrying step (attempt {current_retry + 1}/{max_retries})")
            return executor_fn(step)
        return False


class AlternativeToolStrategy(RecoveryStrategy):
    """Attempts to use an alternative tool if the primary is missing."""
    
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def can_handle(self, result: ReflectionResult, step: Dict[str, Any]) -> bool:
        return result.recommendation == "alternative_tool" and step.get("action_type") == "OPEN_APPLICATION"
        
    def recover(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        target = step.get("target")
        alternatives = self.registry.get_alternatives(target)
        executor_fn = context.get("executor_fn")
        
        if not alternatives:
            logger.warning(f"No alternatives found for {target}")
            return False
            
        for alt in alternatives:
            logger.info(f"Trying alternative tool: {alt} instead of {target}")
            # Mutate the step for the alternative
            original_target = step["target"]
            original_verif = step.get("verification_target")
            
            step["target"] = alt
            if original_verif is not None:
                step["verification_target"] = alt
                
            success = executor_fn(step)
            if success:
                return True
            # Revert if failed
            step["target"] = original_target
            if original_verif is not None:
                step["verification_target"] = original_verif
            
        return False


class PermissionRecoveryStrategy(RecoveryStrategy):
    """Attempts to recover from permission denied errors by changing paths."""
    
    def can_handle(self, result: ReflectionResult, step: Dict[str, Any]) -> bool:
        return result.recommendation == "permission_recovery"
        
    def recover(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        target = step.get("target", "")
        executor_fn = context.get("executor_fn")
        
        # If we failed to write/create in a restricted dir, fallback to a temp or user dir
        # In this simplistic demo implementation, we fallback to a known writable location: $TEMP
        import tempfile
        filename = os.path.basename(target)
        fallback_path = os.path.join(tempfile.gettempdir(), filename)
        
        logger.info(f"Permission denied on {target}. Falling back to {fallback_path}")
        original_target = step["target"]
        original_verif = step.get("verification_target")
        
        step["target"] = fallback_path
        if original_verif is not None:
            step["verification_target"] = fallback_path
            
        success = executor_fn(step)
        if success:
            return True
            
        step["target"] = original_target
        if original_verif is not None:
            step["verification_target"] = original_verif
        return False


class AbortStrategy(RecoveryStrategy):
    """Aborts execution cleanly."""
    
    def can_handle(self, result: ReflectionResult, step: Dict[str, Any]) -> bool:
        return result.recommendation == "abort" or not result.recoverable
        
    def recover(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        logger.warning("Aborting step execution.")
        return False


class RecoveryPlanner:
    """Selects and executes the appropriate recovery strategy."""
    
    def __init__(self, registry: CapabilityRegistry):
        self.strategies: List[RecoveryStrategy] = [
            AlternativeToolStrategy(registry),
            PermissionRecoveryStrategy(),
            RetryStrategy(),
            AbortStrategy()
        ]

    def register_strategy(self, strategy: RecoveryStrategy):
        """Allow extending strategies dynamically."""
        self.strategies.insert(0, strategy)

    def plan_and_recover(self, result: ReflectionResult, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Find the right strategy and execute it."""
        for strategy in self.strategies:
            if strategy.can_handle(result, step):
                logger.info(f"Recovery Planner chose strategy: {strategy.__class__.__name__}")
                return strategy.recover(step, context)
                
        logger.warning("No suitable recovery strategy found.")
        return False
