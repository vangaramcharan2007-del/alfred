"""TTS Engine — real pyttsx3-based text-to-speech for Alfred voice output."""
import pyttsx3
import logging

logger = logging.getLogger(__name__)


class TTSEngine:
    """Synchronous offline TTS using pyttsx3 (SAPI5 on Windows)."""

    def __init__(self):
        self._engine = pyttsx3.init()
        self._configure_voice()

    def _configure_voice(self):
        """Attempt to select the most natural male voice available."""
        voices = self._engine.getProperty("voices")
        selected = None

        # Prefer a male English voice (David on Windows)
        for v in voices:
            name_lower = v.name.lower()
            if "david" in name_lower:
                selected = v
                break

        # Fallback: first English voice
        if selected is None:
            for v in voices:
                if "english" in v.name.lower() or "en" in (v.id or "").lower():
                    selected = v
                    break

        if selected:
            self._engine.setProperty("voice", selected.id)
            logger.info(f"TTS voice selected: {selected.name}")

        # Slightly slower rate for clarity
        self._engine.setProperty("rate", 165)
        self._engine.setProperty("volume", 1.0)

    def speak(self, text: str):
        """Speak the given text through system speakers (blocking)."""
        logger.info(f"Alfred speaks: {text}")
        self._engine.say(text)
        self._engine.runAndWait()

    def list_voices(self):
        """Return a list of available system voice names."""
        voices = self._engine.getProperty("voices")
        return [v.name for v in voices]

    def get_current_voice(self) -> str:
        """Return the name of the currently selected voice."""
        current_id = self._engine.getProperty("voice")
        voices = self._engine.getProperty("voices")
        for v in voices:
            if v.id == current_id:
                return v.name
        return "Unknown"
