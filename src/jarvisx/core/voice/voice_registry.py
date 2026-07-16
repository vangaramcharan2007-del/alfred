import yaml
from pathlib import Path

class VoiceRegistry:
    def __init__(self, config_path: str = "config/voices.yaml"):
        self.config_path = Path(config_path)
        self.voices = {}
        self.load()

    def load(self):
        if not self.config_path.exists():
            return
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            self.voices = {k.lower(): v for k, v in data.items()}

    def get_voice_config(self, personality_name: str) -> dict:
        """Returns the voice configuration for a specific personality, or defaults."""
        name = personality_name.lower()
        if name in self.voices:
            return self.voices[name]
            
        # Fallback to Alfred if missing
        if "alfred" in self.voices:
            return self.voices["alfred"]
            
        # Hardcoded fallback
        return {
            "provider": "piper",
            "voice": "en_us_lessac_medium",
            "speed": 1.0,
            "personality": "neutral"
        }
