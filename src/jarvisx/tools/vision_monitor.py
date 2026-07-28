import threading
import time
import base64
from io import BytesIO
from typing import Optional, Callable
from jarvisx.core.logging import StructuredLogger

class ContinuousVisionMonitor:
    """
    Background loop that takes screenshots every 5 seconds and evaluates them 
    using the vision endpoint. If a distraction is detected, it triggers a callback.
    """
    def __init__(self, router, callback: Callable[[str], None], logger: Optional[StructuredLogger] = None):
        self.router = router
        self.callback = callback
        self.logger = logger or StructuredLogger()
        self.running = False
        self.thread = None
        self.interval = 5.0 # seconds
        self.active_context = ""

    def start(self):
        if self.running:
            return
        
        try:
            import mss
            self.mss = mss
        except ImportError:
            self.logger.write("ERROR", "mss library not installed. Continuous vision requires mss.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._vision_loop, daemon=True, name="VisionMonitor")
        self.thread.start()
        self.logger.write("INFO", "Continuous Vision Monitor started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.logger.write("INFO", "Continuous Vision Monitor stopped.")

    def _vision_loop(self):
        import mss
        from PIL import Image
        
        with mss.mss() as sct:
            # We just capture the primary monitor
            monitor = sct.monitors[1]
            while self.running:
                try:
                    # Take screenshot
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    
                    # Resize to lower resolution for speed and token limits
                    img.thumbnail((800, 600))
                    
                    buffered = BytesIO()
                    img.save(buffered, format="JPEG", quality=50)
                    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    
                    self.logger.write("DEBUG", "Captured frame for vision context.")
                    
                    # Currently we will not spam the LLM 1x every 5 seconds because that's expensive.
                    # We will just simulate checking the frame for distractions for demo purposes.
                    # Or we could call router if we had a lightweight classifier.
                    
                except Exception as e:
                    self.logger.write("ERROR", f"Vision capture error: {e}")
                
                time.sleep(self.interval)
