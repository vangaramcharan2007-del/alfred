import os
import yaml
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manages YAML configuration loading with environments and local overrides."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        
        # Determine environment, default to development
        self.env = os.environ.get("JARVIS_ENV", "development")
        self.load()

    def load(self):
        """Loads base environment config and overlays local.yaml if it exists."""
        env_config_path = self.config_dir / f"{self.env}.yaml"
        local_config_path = self.config_dir / "local.yaml"

        if env_config_path.exists():
            with open(env_config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
                
        if local_config_path.exists():
            with open(local_config_path, "r") as f:
                local_config = yaml.safe_load(f) or {}
                self._deep_merge(self.config, local_config)

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]):
        """Deep merge dictionaries recursively."""
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g. 'node.name')."""
        keys = key.split(".")
        val = self.config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val
