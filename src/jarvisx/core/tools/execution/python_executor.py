import sys
import tempfile
import os
import logging
from typing import Dict, Any
from .command_executor import CommandExecutor
from .permissions import PermissionManager, TrustLevel

logger = logging.getLogger(__name__)

class PythonExecutor:
    @staticmethod
    def execute(code: str, timeout: int = 30) -> Dict[str, Any]:
        PermissionManager.check_permission(TrustLevel.LEVEL_4_SHELL)
        
        # Write to temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".py", text=True)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            
            executable = sys.executable
            command = f'"{executable}" "{temp_path}"'
            logger.info(f"Executing Python script via {command}")
            
            result = CommandExecutor.execute(command, timeout=timeout)
            return result
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
