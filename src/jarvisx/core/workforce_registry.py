import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("WorkforceRegistry")

class WorkforceRegistry:
    """
    Maintains available specialists and capabilities for the Agent Orchestrator workforce.
    """
    def __init__(self, registry_file: Optional[str] = None):
        self.registry_file = registry_file
        self.agents: Dict[str, dict] = self._default_registry()
        
        if self.registry_file:
            self._load_registry()

    def _default_registry(self) -> dict:
        return {
            "backend_agent": {
                "capabilities": ["fastapi", "supabase", "sqlalchemy", "python"]
            },
            "frontend_agent": {
                "capabilities": ["react", "typescript", "tailwind", "nextjs"]
            },
            "testing_agent": {
                "capabilities": ["pytest", "integration_tests", "jest", "cypress"]
            },
            "documentation_agent": {
                "capabilities": ["markdown", "mkdocs", "docstrings", "openapi"]
            },
            "devops_agent": {
                "capabilities": ["docker", "github_actions", "kubernetes", "terraform"]
            },
            "security_agent": {
                "capabilities": ["sast", "dast", "dependency_scanning", "iam"]
            },
            "refactoring_agent": {
                "capabilities": ["code_smells", "linting", "type_hints", "optimization"]
            }
        }

    def _load_registry(self):
        try:
            with open(self.registry_file, 'r') as f:
                custom_agents = json.load(f)
                self.agents.update(custom_agents)
            logger.info(f"Loaded {len(custom_agents)} agents from custom registry.")
        except FileNotFoundError:
            logger.warning(f"Registry file {self.registry_file} not found. Using defaults.")
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")

    def get_agent_capabilities(self, agent_name: str) -> List[str]:
        agent = self.agents.get(agent_name)
        if agent:
            return agent.get("capabilities", [])
        return []

    def find_agent_for_capability(self, capability: str) -> Optional[str]:
        for agent_name, details in self.agents.items():
            if capability in details.get("capabilities", []):
                return agent_name
        return None

    def get_all_agents(self) -> List[str]:
        return list(self.agents.keys())
