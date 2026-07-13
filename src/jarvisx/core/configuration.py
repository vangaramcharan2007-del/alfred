from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional
import keyring
import json

from jarvisx.tools.operational_db import OperationalDatabase


DEFAULT_CONFIG: dict[str, Any] = {
    "setup_completed": False,
    "providers": {
        "llm": {
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen2.5:7b"
        },
        "tts": {},
        "stt": {},
        "memory": {}
    },
    "personalities": {
        "alfred": {
            "agent_id": "alfred",
            "name": "Alfred",
            "tone": "calm executive",
            "style": "decisive, concise, and orchestration-focused",
            "verbosity": "adaptive",
            "warmth": "measured",
            "notes": "Coordinates work without performing specialist tasks directly."
        },
        "edith": {
            "agent_id": "edith",
            "name": "Edith",
            "tone": "brief mobile companion",
            "style": "practical, lightweight, and action-aware",
            "verbosity": "compact",
            "warmth": "friendly",
            "notes": "Keeps mobile interactions direct and locally executable."
        },
        "hermes": {
            "agent_id": "hermes",
            "name": "Hermes",
            "tone": "neutral event courier",
            "style": "structured, quiet, and trace-oriented",
            "verbosity": "minimal",
            "warmth": "neutral",
            "notes": "Carries events and never makes decisions."
        },
        "friday": {
            "agent_id": "friday",
            "name": "Friday",
            "tone": "energetic companion",
            "style": "highly conversational, energetic, proactive",
            "verbosity": "chatty",
            "warmth": "warm",
            "notes": "First-class personality. Proactive and socially aware."
        }
    },
    "voices": {
        "alfred": {"provider": "elevenlabs", "voice_id": "deep_mentor", "speed": 1.0, "emotion": "calm"},
        "edith": {"provider": "elevenlabs", "voice_id": "warm_conversational", "speed": 1.1, "emotion": "warm"},
        "friday": {"provider": "elevenlabs", "voice_id": "energetic_playful", "speed": 1.2, "emotion": "energetic"},
        "hermes": {"provider": "piper", "voice_id": "concise_efficient", "speed": 1.0, "emotion": "neutral"}
    },
    "gui": {
        "theme": "dark",
        "colors": "default",
        "layout": "default"
    },
    "autonomy_levels": {
        "global": 1
    }
}


class ConfigurationManager:
    def __init__(self, op_db: OperationalDatabase) -> None:
        self.op_db = op_db
        self.config_key = "jarvis_config"
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        existing = self.op_db.get(self.config_key)
        if not existing:
            self.op_db.set(self.config_key, deepcopy(DEFAULT_CONFIG))
            return

        # Deep merge defaults into existing
        merged = self._deep_merge(deepcopy(DEFAULT_CONFIG), existing)
        
        # Migrate old keys to keyring
        self._migrate_keys_to_keyring(merged)
        
        if merged != existing:
            self.op_db.set(self.config_key, merged)

    def _migrate_keys_to_keyring(self, config: dict[str, Any]) -> None:
        """Move any plaintext keys found in config over to the OS keyring."""
        # LLM
        llm = config.get("providers", {}).get("llm", {})
        if "openai_api_key" in llm and llm["openai_api_key"]:
            self.set_secure_key("openai_api_key", llm.pop("openai_api_key"))
        if "gemini_api_key" in llm and llm["gemini_api_key"]:
            self.set_secure_key("gemini_api_key", llm.pop("gemini_api_key"))
            
        # TTS
        tts = config.get("providers", {}).get("tts", {})
        if "elevenlabs_api_key" in tts and tts["elevenlabs_api_key"]:
            self.set_secure_key("elevenlabs_api_key", tts.pop("elevenlabs_api_key"))
            
        # MEMORY
        memory = config.get("providers", {}).get("memory", {})
        if "supabase_key" in memory and memory["supabase_key"]:
            self.set_secure_key("supabase_key", memory.pop("supabase_key"))

    def set_secure_key(self, key_name: str, value: str) -> None:
        if value:
            keyring.set_password("JarvisX", key_name, value)
            
    def get_secure_key(self, key_name: str) -> Optional[str]:
        return keyring.get_password("JarvisX", key_name)

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                base[k] = self._deep_merge(base[k], v)
            else:
                base[k] = v
        return base

    def get_config(self) -> dict[str, Any]:
        config = self.op_db.get(self.config_key) or deepcopy(DEFAULT_CONFIG)
        # Inject secure keys into the returned config dictionary dynamically so the rest of the app doesn't need to know about keyring
        if "providers" not in config:
            config["providers"] = {"llm": {}, "tts": {}, "stt": {}, "memory": {}}
            
        openai_key = self.get_secure_key("openai_api_key")
        if openai_key:
            config["providers"]["llm"]["openai_api_key"] = openai_key
            
        gemini_key = self.get_secure_key("gemini_api_key")
        if gemini_key:
            config["providers"]["llm"]["gemini_api_key"] = gemini_key
            
        elevenlabs_key = self.get_secure_key("elevenlabs_api_key")
        if elevenlabs_key:
            config["providers"]["tts"]["elevenlabs_api_key"] = elevenlabs_key
            
        supabase_key = self.get_secure_key("supabase_key")
        if supabase_key:
            config["providers"]["memory"]["supabase_key"] = supabase_key
            
        return config

    def set_config(self, config: dict[str, Any]) -> None:
        # Strip secure keys before saving to DB
        config_to_save = deepcopy(config)
        self._migrate_keys_to_keyring(config_to_save)
        self.op_db.set(self.config_key, config_to_save)

    def get(self, path: str, default: Any = None) -> Any:
        keys = path.split('.')
        val = self.get_config()
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return default
        return val

    def set(self, path: str, value: Any) -> None:
        keys = path.split('.')
        config = self.get_config()
        current = config
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        self.set_config(config)

    @property
    def is_setup_completed(self) -> bool:
        return bool(self.get("setup_completed", False))

    def complete_setup(self) -> None:
        self.set("setup_completed", True)
