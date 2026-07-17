import os
import subprocess
import logging
from .permissions import PermissionManager, TrustLevel
from .command_executor import CommandExecutor

logger = logging.getLogger(__name__)

class AppLauncher:
    @staticmethod
    def launch(app_name: str) -> bool:
        PermissionManager.check_permission(TrustLevel.LEVEL_2_APPS)
        logger.info(f"Launching application: {app_name}")
        try:
            # Basic fallback for Windows apps like 'notepad' or 'code'
            os.startfile(app_name)
            return True
        except Exception as e:
            logger.error(f"Failed to launch {app_name} via startfile: {e}")
            # Try running as shell command
            result = CommandExecutor.execute(f"start {app_name}")
            return result["success"]

    @staticmethod
    def close(process_name: str) -> bool:
        PermissionManager.check_permission(TrustLevel.LEVEL_2_APPS)
        logger.info(f"Closing application: {process_name}")
        if not process_name.endswith(".exe"):
            process_name += ".exe"
        result = CommandExecutor.execute(f"taskkill /IM {process_name} /F")
        return result["success"]

    @staticmethod
    def is_running(process_name: str) -> bool:
        PermissionManager.check_permission(TrustLevel.LEVEL_2_APPS)
        if not process_name.endswith(".exe"):
            process_name += ".exe"
        result = CommandExecutor.execute(f"tasklist /FI \"IMAGENAME eq {process_name}\"")
        return process_name.lower() in result["stdout"].lower()

    @staticmethod
    def focus(process_name: str) -> bool:
        """
        Stub for focusing. Proper focus requires pygetwindow or win32gui which are not installed.
        We will rely on launch to bring it forward if possible.
        """
        PermissionManager.check_permission(TrustLevel.LEVEL_2_APPS)
        logger.info(f"Focusing application: {process_name}")
        return AppLauncher.launch(process_name)
