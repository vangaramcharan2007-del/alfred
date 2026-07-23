import os
from pathlib import Path
from dotenv import load_dotenv
import json

class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        # 1. Load .env
        load_dotenv()
        
        # 2. Determine environment
        self.ENV = os.environ.get("JARVIS_ENV", "development")
        self.IS_OFFLINE = os.environ.get("JARVIS_OFFLINE", "false").lower() == "true"
        
        # 3. Provider settings
        self.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        self.ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
        
        # 4. Agent and DB settings
        self.DB_PATH = Path(os.environ.get("DB_PATH", "databases/objectives.db"))
        self.VAULT_PATH = Path(os.environ.get("VAULT_PATH", "vault/"))
        
        # 5. Load dynamic config from configs/ based on environment if it exists
        env_config = Path(f"configs/{self.ENV}.json")
        self.extra_config = {}
        if env_config.exists():
            try:
                with open(env_config, 'r') as f:
                    self.extra_config = json.load(f)
            except Exception:
                pass

    def get(self, key, default=None):
        return self.extra_config.get(key, os.environ.get(key, default))

settings = Settings()
