import os
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class WorkflowManager:
    """
    Manages reusable execution patterns (workflows).
    Saves successful workflows for future use by Alfred.
    """
    
    def __init__(self, workspace_path: str = "workspace"):
        self.workspace_path = workspace_path
        self.workflows_dir = os.path.join(self.workspace_path, "workflows")
        self._ensure_workspace()
        
    def _ensure_workspace(self):
        """Creates the necessary workspace directories if they don't exist."""
        directories = [
            self.workspace_path,
            self.workflows_dir,
            os.path.join(self.workspace_path, "skills"),
            os.path.join(self.workspace_path, "knowledge"),
            os.path.join(self.workspace_path, "experiments")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
    def save_workflow(self, name: str, steps: List[str], metadata: Dict[str, Any] = None):
        """
        Saves a successful workflow pattern.
        """
        if not metadata:
            metadata = {}
            
        workflow = {
            "name": name,
            "steps": steps,
            "metadata": metadata
        }
        
        # Replace spaces with underscores for safe filenames
        filename = f"{name.replace(' ', '_').lower()}.json"
        filepath = os.path.join(self.workflows_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(workflow, f, indent=4)
            logger.info(f"Saved reusable workflow: {name}")
        except Exception as e:
            logger.error(f"Failed to save workflow {name}: {e}")
            
    def get_workflow(self, name: str) -> Dict[str, Any]:
        """
        Loads a saved workflow by name.
        """
        filename = f"{name.replace(' ', '_').lower()}.json"
        filepath = os.path.join(self.workflows_dir, filename)
        
        if not os.path.exists(filepath):
            return {}
            
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workflow {name}: {e}")
            return {}
            
    def list_workflows(self) -> List[str]:
        """
        Lists all available saved workflows.
        """
        workflows = []
        if os.path.exists(self.workflows_dir):
            for filename in os.listdir(self.workflows_dir):
                if filename.endswith(".json"):
                    workflows.append(filename[:-5].replace("_", " ").title())
        return workflows
