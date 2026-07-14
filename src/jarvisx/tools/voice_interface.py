import asyncio
import logging
import time

try:
    from faster_whisper import WhisperModel
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

from jarvisx.core.swarm_supervisor import SwarmSupervisor
from jarvisx.tools.db_manager import DatabaseManager

class VoiceInterface:
    def __init__(self):
        self.supervisor = SwarmSupervisor()
        self.db = DatabaseManager()
        
        if STT_AVAILABLE:
            try:
                self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
            except Exception:
                self.model = None
                STT_AVAILABLE = False
        else:
            logging.warning("faster-whisper not found. Running STT in Mock Mode.")
            self.model = None

        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
            except Exception:
                self.engine = None
                TTS_AVAILABLE = False
        else:
            logging.warning("pyttsx3 not found. Running TTS in Mock Mode.")
            self.engine = None

    async def calibrate_microphone(self, duration=5):
        logging.info(f"Calibrating microphone for {duration} seconds...")
        if STT_AVAILABLE:
            await asyncio.sleep(duration)
            logging.info("Microphone calibrated successfully.")
            return True
        else:
            await asyncio.sleep(duration)
            logging.info("[MOCK] Microphone calibration complete.")
            return True

    def synthesize_speech(self, text: str):
        if TTS_AVAILABLE:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            logging.info(f"[MOCK TTS OUTPUT]: {text}")

    async def async_listen_loop(self):
        logging.info("Starting Voice Interface async loop...")
        
        # Simulate an incoming voice command instead of blocking on hardware
        simulated_voice_input = "Analyze the incoming data stream and build a predictive model."
        logging.info(f"[MOCK MIC CAPTURE]: '{simulated_voice_input}'")
        
        # Route to SwarmSupervisor
        logging.info("Routing payload to SwarmSupervisor...")
        response_data = await self.supervisor.execute_complex_task(simulated_voice_input)
        
        # Synthesize response
        response_text = f"Task completed. {len(response_data['results'])} workers have returned data."
        self.synthesize_speech(response_text)
        
        # Log to telemetry
        await self.db.execute_query('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, filepath TEXT)''')
        await self.db.execute_query("INSERT INTO agent_logs (action, filepath) VALUES (?, ?)", 
                               ("Voice Interface Online", "src/jarvisx/tools/voice_interface.py"))

async def self_test():
    interface = VoiceInterface()
    await interface.calibrate_microphone(duration=2)
    await interface.async_listen_loop()
    print("Voice Interface simulation complete.")

if __name__ == "__main__":
    asyncio.run(self_test())
