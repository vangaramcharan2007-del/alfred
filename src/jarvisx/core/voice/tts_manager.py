import threading
import queue
import logging
from dataclasses import dataclass, field
from jarvisx.core.voice.tts_engine import TTSEngine

logger = logging.getLogger(__name__)

class TTSPriority:
    STOP = 1
    PERMISSION_REQUEST = 2
    NORMAL = 3

@dataclass(order=True)
class TTSItem:
    priority: int
    text: str = field(compare=False)
    
class TTSManager:
    """
    Manages TTS queue and execution with priorities.
    Runs in a background thread to prevent blocking the main voice loop.
    """
    def __init__(self, dashboard=None):
        self.dashboard = dashboard
        self.engine = TTSEngine()
        self.queue = queue.PriorityQueue()
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                item = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if item.priority == TTSPriority.STOP:
                # Flush the queue
                while not self.queue.empty():
                    try:
                        self.queue.get_nowait()
                        self.queue.task_done()
                    except queue.Empty:
                        break
                self.queue.task_done()
                continue
            
            if self.dashboard:
                self.dashboard.set_tts(item.text)
            
            try:
                self.engine.speak(item.text)
            except Exception as e:
                logger.error(f"TTS Worker Error: {e}")
                
            if self.dashboard:
                self.dashboard.set_tts("")
                
            self.queue.task_done()

    def speak(self, text: str, priority: int = TTSPriority.NORMAL):
        self.queue.put(TTSItem(priority=priority, text=text))

    def stop(self):
        """Immediately interrupt and clear queue."""
        self.queue.put(TTSItem(priority=TTSPriority.STOP, text=""))

    def shutdown(self):
        self._stop_event.set()
        self._worker_thread.join(timeout=2.0)
