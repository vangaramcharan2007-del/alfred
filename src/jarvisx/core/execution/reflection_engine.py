"""Reflection Engine — evaluates execution outcomes and recommends recovery."""
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

from jarvisx.core.execution.failure_classifier import FailureClassifier, FailureCategory

logger = logging.getLogger(__name__)

@dataclass
class ReflectionResult:
    success: bool
    recoverable: bool = False
    failure_category: Optional[FailureCategory] = None
    recommendation: str = "none"
    confidence: float = 1.0


class ReflectionEngine:
    """Analyzes step outcomes to determine success or failure recovery paths."""
    
    def __init__(self, classifier: FailureClassifier = None):
        self.classifier = classifier or FailureClassifier()

    def reflect(
        self, 
        step: Dict[str, Any], 
        execution_success: bool, 
        verification_success: bool, 
        error: Optional[Exception] = None
    ) -> ReflectionResult:
        """
        Reflect on a step's execution and produce a result with recommendations.
        """
        # If no errors and verification passed, it's a success
        if execution_success and verification_success and not error:
            return ReflectionResult(success=True)

        # It failed. Classify the failure.
        action = step.get("action_type", "UNKNOWN")
        target = step.get("target", "UNKNOWN")
        
        category = self.classifier.classify(
            action=action, 
            target=target, 
            error=error, 
            verification_failed=not verification_success
        )
        
        # Determine recoverability and recommendation
        recoverable = True
        recommendation = "retry"
        confidence = 0.8
        
        if category == FailureCategory.MISSING_APPLICATION:
            recommendation = "alternative_tool"
            confidence = 0.95
        elif category == FailureCategory.PERMISSION_DENIED:
            recommendation = "permission_recovery"
            confidence = 0.90
        elif category == FailureCategory.VERIFICATION_MISMATCH:
            recommendation = "retry"
            confidence = 0.70
        elif category == FailureCategory.TIMEOUT:
            recommendation = "retry" # Maybe with a longer timeout later
            confidence = 0.85
        elif category == FailureCategory.INVALID_ARGUMENTS:
            recoverable = False
            recommendation = "abort"
            confidence = 0.99
        elif category == FailureCategory.UNKNOWN:
            # Try a simple retry for unknown flaky errors
            recommendation = "retry"
            confidence = 0.50

        logger.info(f"Reflection: {category.name} -> {recommendation} (conf: {confidence})")
        
        return ReflectionResult(
            success=False,
            recoverable=recoverable,
            failure_category=category,
            recommendation=recommendation,
            confidence=confidence
        )
