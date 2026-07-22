"""STT Listener — speech-to-text using the speech_recognition library."""
import logging
import time
from typing import Optional

import speech_recognition as sr
import numpy as np

logger = logging.getLogger(__name__)

try:
    from faster_whisper import WhisperModel
    _HAS_FASTER_WHISPER = True
except ImportError:
    _HAS_FASTER_WHISPER = False

class STTListener:
    """Captures microphone input and returns transcribed text using Whisper or Google fallback."""

    def __init__(self, energy_threshold: int = 300, pause_threshold: float = 0.8):
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = energy_threshold
        self._recognizer.pause_threshold = pause_threshold
        self._recognizer.dynamic_energy_threshold = True
        self._mic = sr.Microphone()
        
        self.use_whisper = _HAS_FASTER_WHISPER
        if self.use_whisper:
            try:
                logger.info("Initializing faster-whisper tiny model...")
                self.whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            except Exception as e:
                logger.error(f"Failed to load faster-whisper: {e}. Falling back to Google STT.")
                self.use_whisper = False

        # Calibrate for ambient noise once
        with self._mic as source:
            logger.info("Calibrating microphone for ambient noise...")
            self._recognizer.adjust_for_ambient_noise(source, duration=1.0)
            logger.info(f"Energy threshold set to {self._recognizer.energy_threshold}")

    def listen(self, timeout: float = 8.0, phrase_time_limit: float = 10.0) -> Optional[str]:
        """Block until the user speaks, then return the transcribed text.

        Returns None if recognition fails or times out.
        """
        try:
            with self._mic as source:
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
            start = time.time()
            if self.use_whisper:
                # Convert AudioData to numpy array for faster-whisper
                wav_bytes = audio.get_wav_data(convert_rate=16000, convert_width=2)
                # Skip wav header (44 bytes) and convert to float32
                audio_np = np.frombuffer(wav_bytes[44:], dtype=np.int16).astype(np.float32) / 32768.0
                segments, info = self.whisper_model.transcribe(audio_np, beam_size=1)
                text = " ".join([segment.text for segment in segments]).strip()
            else:
                text = self._recognizer.recognize_google(audio)
                
            latency_ms = int((time.time() - start) * 1000)
            logger.info(f"STT result ({latency_ms}ms): {text}")
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            logger.error(f"STT service error: {e}")
            return None
        except Exception as e:
            logger.error(f"STT unexpected error: {e}")
            return None
