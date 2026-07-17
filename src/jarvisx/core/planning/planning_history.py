import json
import os
from typing import Dict, Any, List

class PlanningHistory:
    """Persists objectives, generated plans, failures, and outcomes."""
    
    def __init__(self, storage_path: str = "var/planning_history.json"):
        self.storage_path = storage_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.storage_path):
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump([], f)

    def record_session(self, session_data: Dict[str, Any]):
        with open(self.storage_path, "r") as f:
            data = json.load(f)
            
        data.append(session_data)
        
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_history(self) -> List[Dict[str, Any]]:
        with open(self.storage_path, "r") as f:
            return json.load(f)
