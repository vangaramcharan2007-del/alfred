import json
from pathlib import Path
from typing import Dict, Any, List

class AgentDiscovery:
    def __init__(self, manifest_path: str = "src/jarvisx/agents/manifest.json"):
        self.manifest_path = Path(manifest_path)

    def load_manifest(self) -> Dict[str, Any]:
        """Loads the agent manifest file."""
        if not self.manifest_path.exists():
            return {}
        with open(self.manifest_path, "r") as f:
            return json.load(f)

    def get_capabilities(self) -> Dict[str, List[str]]:
        """Returns a mapping of agent_id to their capabilities."""
        manifest = self.load_manifest()
        return {
            agent_id: data.get("capabilities", [])
            for agent_id, data in manifest.items()
        }
