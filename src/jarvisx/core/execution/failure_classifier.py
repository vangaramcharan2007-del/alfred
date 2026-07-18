"""Failure Classifier — maps errors to structured enums."""
import logging
from enum import Enum, auto
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)

class FailureCategory(Enum):
    MISSING_APPLICATION = auto()
    MISSING_EXECUTABLE = auto()
    MISSING_FILE = auto()
    MISSING_FOLDER = auto()
    PERMISSION_DENIED = auto()
    TIMEOUT = auto()
    VERIFICATION_MISMATCH = auto()
    NETWORK_UNAVAILABLE = auto()
    TOOL_EXCEPTION = auto()
    INVALID_ARGUMENTS = auto()
    UNKNOWN = auto()


class FailureClassifier:
    """Classifies execution and verification failures into structured categories."""
    
    @classmethod
    def classify(
        cls, 
        action: str, 
        target: str, 
        error: Optional[Exception] = None, 
        verification_failed: bool = False
    ) -> FailureCategory:
        """Analyze the context to classify the failure."""
        
        # 1. Check explicit exceptions
        if error is not None:
            err_str = str(error).lower()
            err_type = type(error).__name__
            
            if isinstance(error, PermissionError) or "permission denied" in err_str:
                return FailureCategory.PERMISSION_DENIED
                
            if isinstance(error, FileNotFoundError) or "no such file" in err_str:
                if action == "OPEN_APPLICATION" or action == "LAUNCH":
                    return FailureCategory.MISSING_APPLICATION
                elif "folder" in action.lower() or "dir" in action.lower():
                    return FailureCategory.MISSING_FOLDER
                else:
                    return FailureCategory.MISSING_FILE
                    
            if isinstance(error, TimeoutError) or "timeout" in err_str:
                return FailureCategory.TIMEOUT
                
            if "network" in err_str or "connection" in err_str or "socket" in err_str:
                return FailureCategory.NETWORK_UNAVAILABLE
                
            if isinstance(error, ValueError) or isinstance(error, TypeError):
                return FailureCategory.INVALID_ARGUMENTS
                
            return FailureCategory.TOOL_EXCEPTION

        # 2. If no explicit exception but verification failed
        if verification_failed:
            if action == "OPEN_APPLICATION":
                return FailureCategory.MISSING_APPLICATION
            if action == "SEARCH_GOOGLE" or action == "BROWSER_GOTO":
                return FailureCategory.TIMEOUT
            return FailureCategory.VERIFICATION_MISMATCH
            
        # 3. Fallback
        return FailureCategory.UNKNOWN
