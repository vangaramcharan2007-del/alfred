import logging
import threading
import time
import json
import urllib.request
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class AthenaResearcher:
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
        self.research_file = self.project_dir / "var" / "research" / "dossier.md"

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
        logger.info("[Athena] Autonomous Researcher online.")
        self._thread = threading.Thread(target=self._loop, daemon=True, name="AthenaResearcher")
        self._thread.start()

    def _loop(self):
        while self._running:
            try:
                # Fetch HackerNews Top Stories as a proxy for 'AI & Tech Research'
                req = urllib.request.Request("https://hacker-news.firebaseio.com/v0/topstories.json")
                with urllib.request.urlopen(req) as response:
                    story_ids = json.loads(response.read().decode())[:5] # Get top 5

                dossier_content = f"# Athena Daily Research Dossier\n*Last Updated: {datetime.now().isoformat()}*\n\n"
                
                for sid in story_ids:
                    sreq = urllib.request.Request(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
                    with urllib.request.urlopen(sreq) as sres:
                        story = json.loads(sres.read().decode())
                        title = story.get('title', 'Unknown')
                        url = story.get('url', f"https://news.ycombinator.com/item?id={sid}")
                        dossier_content += f"### [{title}]({url})\n"
                
                with open(self.research_file, "w", encoding="utf-8") as f:
                    f.write(dossier_content)
                
                logger.info("[Athena] Compiled latest web research into var/research/dossier.md.")
                self._push_to_ui("research_event", {"status": "Dossier Updated", "topic": "Global Tech & AI"})
            except Exception as e:
                logger.debug(f"[Athena] Loop error: {e}")
                
            time.sleep(3600) # Run every hour
