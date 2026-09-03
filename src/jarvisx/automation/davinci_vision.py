import logging
import threading
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class DaVinciHandler(FileSystemEventHandler):
    def __init__(self, ui_callback):
        super().__init__()
        self.ui_callback = ui_callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            logger.info(f"[DaVinci] New napkin sketch detected: {Path(event.src_path).name}")
            self.ui_callback("vision_event", {"status": "Analyzing Sketch..."})
            
            # Simulate Gemini Vision parsing the sketch
            time.sleep(3)
            
            # Generate the HTML file
            out_path = Path(event.src_path).with_suffix(".html")
            html_code = f"<html><body><h1>DaVinci Generated UI</h1><p>Mock UI from {Path(event.src_path).name}</p></body></html>"
            
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html_code)
                
            logger.info(f"[DaVinci] Code generation complete. Saved to {out_path.name}")
            self.ui_callback("vision_event", {"status": f"UI Coded: {out_path.name}"})


class DaVinciVision:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self.observer = None
        self.project_dir = Path(__file__).parent.parent.parent.parent.absolute()
        self.sketches_dir = self.project_dir / "var" / "sketches"

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
        logger.info("[DaVinci] Napkin-to-Code Vision Agent online.")
        
        self.observer = Observer()
        event_handler = DaVinciHandler(self._push_to_ui)
        self.observer.schedule(event_handler, str(self.sketches_dir), recursive=False)
        self.observer.start()
