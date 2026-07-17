import psutil
import time
import subprocess
from .desktop_permissions import DesktopPermissionManager, DesktopTrustLevel
from .logger import DesktopLogger

class ProcessManager:
    @staticmethod
    def start_process(command: str) -> bool:
        DesktopPermissionManager.require(DesktopTrustLevel.PROCESS_CONTROL)
        DesktopLogger.log_action("ProcessManager", "START", f"Starting process: {command}")
        
        try:
            # Accessibility-first: Windows specific launch
            proc = subprocess.Popen(command, shell=True)
            time.sleep(2) # State verification delay
            
            # State verification
            if proc.poll() is None:
                DesktopLogger.log_action("ProcessManager", "START_VERIFY", f"Process {command} is running")
                return True
            else:
                DesktopLogger.log_error("ProcessManager", "START_VERIFY", f"Process {command} exited immediately")
                return False
        except Exception as e:
            DesktopLogger.log_error("ProcessManager", "START", str(e))
            raise e

    @staticmethod
    def is_running(process_name: str) -> bool:
        DesktopPermissionManager.require(DesktopTrustLevel.READ_ONLY)
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                return True
        return False

    @staticmethod
    def kill_process(process_name: str) -> bool:
        DesktopPermissionManager.require(DesktopTrustLevel.PROCESS_CONTROL)
        DesktopLogger.log_action("ProcessManager", "KILL", f"Killing process: {process_name}")
        killed = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                try:
                    proc.kill()
                    killed = True
                except psutil.NoSuchProcess:
                    pass
        
        if killed:
            time.sleep(1) # verification delay
            if ProcessManager.is_running(process_name):
                DesktopLogger.log_error("ProcessManager", "KILL_VERIFY", f"Failed to kill {process_name}")
                raise RuntimeError(f"Failed to kill process {process_name}")
            DesktopLogger.log_action("ProcessManager", "KILL_VERIFY", f"Process {process_name} terminated")
        return killed
