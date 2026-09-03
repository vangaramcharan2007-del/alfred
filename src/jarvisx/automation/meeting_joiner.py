import logging
import threading
import time
import json
from pathlib import Path
import webbrowser
from datetime import datetime

logger = logging.getLogger(__name__)

class AutoMeetingJoiner:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread = None
        self.project_dir = Path(__file__).parent.parent.parent.parent.absolute()
        self.calendar_file = self.project_dir / "var" / "calendar.json"
        self._joined_meetings = set()

    def _push_to_ui(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def start(self):
        if self._running:
            return
        self._running = True
        logger.info("[ChronoCommute] Auto-Meeting Joiner online.")
        self._thread = threading.Thread(target=self._loop, daemon=True, name="ChronoCommute")
        self._thread.start()

    def _loop(self):
        while self._running:
            try:
                if self.calendar_file.exists():
                    with open(self.calendar_file, "r") as f:
                        events = json.load(f)
                    
                    now = time.time()
                    for event in events:
                        event_id = event.get("id")
                        target_time = event.get("timestamp", 0)
                        url = event.get("url")
                        
                        # If meeting is in exactly 60 seconds (or less, but in the future)
                        if event_id not in self._joined_meetings and 0 < (target_time - now) <= 60:
                            logger.info(f"[ChronoCommute] Meeting '{event.get('title')}' starting in 1 minute. Opening URL.")
                            self._push_to_ui("meeting_event", {"title": event.get("title"), "url": url})
                            webbrowser.open(url)
                            self._joined_meetings.add(event_id)
            except Exception as e:
                logger.debug(f"[ChronoCommute] Loop error: {e}")
                
            time.sleep(10)
