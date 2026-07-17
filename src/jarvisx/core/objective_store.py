import os
import json
import time
import shutil
from typing import Dict, Any, List

class ObjectiveStore:
    """Manages persistence of objectives to disk across sessions."""
    
    BASE_DIR = "var/objectives"
    ACTIVE_DIR = os.path.join(BASE_DIR, "active")
    COMPLETED_DIR = os.path.join(BASE_DIR, "completed")
    FAILED_DIR = os.path.join(BASE_DIR, "failed")

    def __init__(self):
        self._ensure_directories()

    def _ensure_directories(self):
        for d in [self.ACTIVE_DIR, self.COMPLETED_DIR, self.FAILED_DIR]:
            os.makedirs(d, exist_ok=True)

    def _get_path(self, objective_id: str, directory: str) -> str:
        return os.path.join(directory, f"{objective_id}.json")

    def save_objective(self, obj_data: Dict[str, Any]):
        """Save a new or existing objective."""
        objective_id = obj_data.get("objective_id")
        if not objective_id:
            raise ValueError("Objective data must contain 'objective_id'")
        
        obj_data["updated_at"] = time.time()
        if "created_at" not in obj_data:
            obj_data["created_at"] = time.time()
            
        path = self._get_path(objective_id, self.ACTIVE_DIR)
        with open(path, "w") as f:
            json.dump(obj_data, f, indent=2)

    def load_active_objectives(self) -> List[Dict[str, Any]]:
        """Load all currently active objectives."""
        objectives = []
        if os.path.exists(self.ACTIVE_DIR):
            for filename in os.listdir(self.ACTIVE_DIR):
                if filename.endswith(".json"):
                    path = os.path.join(self.ACTIVE_DIR, filename)
                    try:
                        with open(path, "r") as f:
                            obj_data = json.load(f)
                            objectives.append(obj_data)
                    except Exception as e:
                        print(f"Error loading {path}: {e}")
        return objectives

    def update_objective(self, objective_id: str, updates: Dict[str, Any]):
        """Update specific fields of an active objective."""
        path = self._get_path(objective_id, self.ACTIVE_DIR)
        if not os.path.exists(path):
            return
            
        with open(path, "r") as f:
            obj_data = json.load(f)
            
        obj_data.update(updates)
        obj_data["updated_at"] = time.time()
        
        with open(path, "w") as f:
            json.dump(obj_data, f, indent=2)

    def complete_objective(self, objective_id: str):
        """Move objective to completed directory."""
        src = self._get_path(objective_id, self.ACTIVE_DIR)
        dst = self._get_path(objective_id, self.COMPLETED_DIR)
        if os.path.exists(src):
            self.update_objective(objective_id, {"status": "COMPLETED", "progress": 100})
            shutil.move(src, dst)

    def fail_objective(self, objective_id: str):
        """Move objective to failed directory."""
        src = self._get_path(objective_id, self.ACTIVE_DIR)
        dst = self._get_path(objective_id, self.FAILED_DIR)
        if os.path.exists(src):
            self.update_objective(objective_id, {"status": "FAILED"})
            shutil.move(src, dst)
