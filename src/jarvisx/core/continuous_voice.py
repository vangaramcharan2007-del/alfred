import threading
import time
import logging
import os
import sys

logger = logging.getLogger(__name__)

class ContinuousVoiceEngine:
    """
    Maintains an open microphone loop to listen for the wake word ('Friday') 
    and handles background TTS interaction for the Apex Protocol.
    """
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.thread = None
        self.debug_mode = os.environ.get("JARVIS_SIMULATION_MODE", "1") == "1"

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True, name="FridayVoiceMic")
        self.thread.start()
        logger.info("Continuous Voice Engine started. Open mic active.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("Continuous Voice Engine stopped.")

    def _listen_loop(self):
        # In a real environment, this would use speech_recognition or pyaudio
        # For the Jarvis X simulation, we mock the background detection
        while self.running:
            time.sleep(1.0)
            
            if self.debug_mode:
                # We check a mock file for injected "voice" commands for the live demo
                demo_file = os.path.join("scratch", "voice_inject.txt")
                if os.path.exists(demo_file):
                    try:
                        with open(demo_file, "r", encoding="utf-8") as f:
                            text = f.read().strip()
                        if text:
                            logger.info(f"[Mic Captured] {text}")
                            # Clear the file
                            open(demo_file, "w").close()
                            
                            # Trigger the callback with the detected text
                            if "friday" in text.lower():
                                self.callback(text)
                    except Exception as e:
                        pass
