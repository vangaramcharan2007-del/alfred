import threading
import time
import logging
import os
import sys
import asyncio

try:
    from jarvisx.ui.client import set_overlay_color
except ImportError:
    def set_overlay_color(color): pass

logger = logging.getLogger(__name__)

class ContinuousVoiceEngine:
    """
    Maintains an open microphone loop to listen for the wake word ('Friday' or 'Alfred') 
    and handles background TTS interaction for the Apex Protocol.
    """
    def __init__(self, runtime):
        self.runtime = runtime
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
        
    def _handle_voice_command(self, text):
        logger.info(f"Processing voice command: {text}")
        
        # We need an event loop to run the async orchestrator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Process via Alfred
            response = loop.run_until_complete(self.runtime.alfred.process(text))
            
            # Send color update to the overlay based on the agent that handled it
            if response and hasattr(response, 'agent_id'):
                set_overlay_color(response.agent_id)
            else:
                set_overlay_color("alfred")
                
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            set_overlay_color("error")
        finally:
            loop.close()
            # Revert to default color after a delay (simulating end of speech)
            time.sleep(3)
            set_overlay_color("friday") # Default fallback state

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
                            
                            # Trigger the processor in a separate thread so we don't block the mic
                            threading.Thread(target=self._handle_voice_command, args=(text,), daemon=True).start()
                    except Exception as e:
                        pass
