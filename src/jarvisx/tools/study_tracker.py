import time
import threading
from typing import Optional

from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.base import BaseTool, ToolResult

class StudyTrackerTool(BaseTool):
    name = "study_tracker"

    def __init__(self, guardian, logger: Optional[StructuredLogger] = None):
        self.guardian = guardian
        self.logger = logger
        self.timer_thread = None

    def start_focus_session(self, duration_minutes: int, vision_monitor=None) -> ToolResult:
        if self.timer_thread and self.timer_thread.is_alive():
            return ToolResult(success=False, message="A focus session is already running.")
            
        self.guardian.start()
        self.guardian.engage_focus_mode()
        
        if vision_monitor:
            vision_monitor.start()
        
        self.timer_thread = threading.Thread(
            target=self._run_timer, 
            args=(duration_minutes, vision_monitor),
            daemon=True
        )
        self.timer_thread.start()
        
        if self.logger:
            self.logger.write("INFO", f"Started focus session for {duration_minutes} minutes.")
            
        return ToolResult(
            success=True, 
            message=f"Focus session started. Guardian engaged for {duration_minutes} minutes."
        )

    def _run_timer(self, duration_minutes: int, vision_monitor=None):
        # We can scale this to hours, but using seconds for debug if needed.
        time.sleep(duration_minutes * 60)
        self.guardian.disengage_focus_mode()
        
        if vision_monitor:
            vision_monitor.stop()
            
        if self.logger:
            self.logger.write("INFO", "Focus session completed. Guardian disengaged.")
