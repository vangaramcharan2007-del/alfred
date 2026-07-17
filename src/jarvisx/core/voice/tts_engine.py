"""TTS Engine — pyttsx3-based text-to-speech for Alfred voice output.

Root-cause fix: pyttsx3's internal COM event loop gets stuck after repeated
runAndWait() calls on Windows SAPI5.  The stable fix is to re-create the
engine for every utterance so COM state is always clean.
"""
import pyttsx3
import logging

logger = logging.getLogger(__name__)

# Detect preferred voice once at module load so we don't scan every call.
_PREFERRED_VOICE_ID = None


def _find_preferred_voice():
    """Scan voices once and cache the preferred voice ID."""
    global _PREFERRED_VOICE_ID
    if _PREFERRED_VOICE_ID is not None:
        return
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        for v in voices:
            if "david" in v.name.lower():
                _PREFERRED_VOICE_ID = v.id
                logger.info(f"TTS preferred voice: {v.name}")
                engine.stop()
                return
        for v in voices:
            if "english" in v.name.lower():
                _PREFERRED_VOICE_ID = v.id
                logger.info(f"TTS fallback voice: {v.name}")
                engine.stop()
                return
        if voices:
            _PREFERRED_VOICE_ID = voices[0].id
        engine.stop()
    except Exception as e:
        logger.error(f"Voice scan failed: {e}")


_find_preferred_voice()


class TTSEngine:
    """Reliable offline TTS — recreates pyttsx3 engine per utterance to avoid
    the SAPI5 runAndWait() stall bug."""

    def __init__(self):
        # Verify voice availability at init time
        self._voice_id = _PREFERRED_VOICE_ID

    def speak(self, text: str):
        """Speak the given text through system speakers (blocking).

        A fresh engine is created each time to guarantee audio output.
        """
        engine = None
        try:
            engine = pyttsx3.init()
            if self._voice_id:
                engine.setProperty("voice", self._voice_id)
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 1.0)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS speak failed: {e}")
        finally:
            if engine:
                try:
                    engine.stop()
                except Exception:
                    pass

    def list_voices(self):
        """Return a list of available system voice names."""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            names = [v.name for v in voices]
            engine.stop()
            return names
        except Exception:
            return []

    def get_current_voice(self) -> str:
        """Return the name of the currently selected voice."""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            engine.stop()
            for v in voices:
                if v.id == self._voice_id:
                    return v.name
        except Exception:
            pass
        return "Unknown"
