import json
import os
from pathlib import Path
from typing import Any, Dict

STATE_DIR = Path("var/state")
AGENTS_STATE_FILE = STATE_DIR / "agents.json"

def _ensure_state_file() -> None:
    if not STATE_DIR.exists():
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not AGENTS_STATE_FILE.exists():
        with open(AGENTS_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def get_agent_state(agent_id: str) -> Dict[str, Any]:
    _ensure_state_file()
    try:
        with open(AGENTS_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(agent_id, {})
    except Exception:
        return {}

def update_agent_state(agent_id: str, key: str, value: Any) -> None:
    _ensure_state_file()
    try:
        with open(AGENTS_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
        
    if agent_id not in data:
        data[agent_id] = {}
        
    data[agent_id][key] = value
    
    with open(AGENTS_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
