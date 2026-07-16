import logging
import asyncio

try:
    import pyaudio
    import numpy as np
    from openwakeword.model import Model
    HAS_OPENWAKEWORD = True
except ImportError:
    HAS_OPENWAKEWORD = False

logger = logging.getLogger(__name__)

class WakeEngine:
    def __init__(self, threshold: float = 0.70):
        self.threshold = threshold
        self.model = None
        self.audio = None
        self.stream = None
        self.is_running = False

    def initialize(self):
        if not HAS_OPENWAKEWORD:
            logger.warning("openwakeword or pyaudio is missing. Wake engine disabled.")
            return

        try:
            # openwakeword includes a pre-trained "alexa", "hey mycroft", "hey jarvis" models.
            # We'll use a generic fallback for 'alfred' if we don't have a custom ONNX.
            # For this MVP, we load the default "hey jarvis" model or fallback.
            self.model = Model(wakeword_models=["hey jarvis"], inference_framework="onnx")
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1280
            )
            logger.info("WakeEngine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize WakeEngine: {e}")

    async def wait_for_wake(self) -> bool:
        """Blocks until the wake word is detected."""
        if not self.model or not self.stream:
            # Fallback for systems without audio hardware or models:
            # Just wait forever or rely on push-to-talk.
            await asyncio.sleep(86400)
            return False

        self.is_running = True
        logger.info("Listening for wake word...")

        while self.is_running:
            try:
                # Read audio block
                data = self.stream.read(1280, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Feed to model
                prediction = self.model.predict(audio_data)
                
                # Check thresholds
                for mdl, score in prediction.items():
                    if score >= self.threshold:
                        logger.info(f"Wake word detected! Score: {score}")
                        return True
                        
                await asyncio.sleep(0.01) # Yield to event loop
            except Exception as e:
                logger.error(f"Error in wake word detection: {e}")
                await asyncio.sleep(1)

        return False

    def stop(self):
        self.is_running = False

    def cleanup(self):
        self.stop()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
