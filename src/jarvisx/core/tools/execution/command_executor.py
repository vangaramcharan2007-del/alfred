import subprocess
import time
import logging
from typing import Dict, Any, Optional
from .permissions import PermissionManager, TrustLevel

logger = logging.getLogger(__name__)

class CommandExecutor:
    @staticmethod
    def execute(command: str, timeout: int = 30, cwd: Optional[str] = None) -> Dict[str, Any]:
        PermissionManager.check_permission(TrustLevel.LEVEL_4_SHELL)
        start_time = time.time()
        logger.info(f"Executing command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "return_code": result.returncode,
                "duration_ms": duration_ms
            }
        except subprocess.TimeoutExpired as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Command timed out: {command}")
            return {
                "success": False,
                "stdout": e.stdout.decode('utf-8') if getattr(e, 'stdout', None) else "",
                "stderr": f"Timeout after {timeout} seconds",
                "return_code": -1,
                "duration_ms": duration_ms
            }
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Command execution error: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -2,
                "duration_ms": duration_ms
            }
