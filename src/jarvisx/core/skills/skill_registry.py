from typing import Dict, List, Optional
import logging
from jarvisx.core.skills.skill import BaseSkill

logger = logging.getLogger(__name__)

class SkillRegistry:
    """
    Central repository for discovering and managing installed skills.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.skills = {}
        return cls._instance

    def register(self, skill: BaseSkill):
        """Registers a skill in the intelligence layer."""
        if skill.name in self.skills:
            logger.warning(f"Skill {skill.name} is already registered. Overwriting.")
        self.skills[skill.name] = skill
        logger.info(f"Registered skill: {skill.name}")

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """Retrieves a skill by name."""
        return self.skills.get(name)

    def list_capabilities(self) -> str:
        """
        Formats all available skills as a capability string for discovery.
        Example output:
        Available:
        ✓ Coding Assistant
        ✓ Research Assistant
        """
        if not self.skills:
            return "No skills currently installed."
            
        capabilities = ["Available Skills:"]
        for name, skill in self.skills.items():
            capabilities.append(f"✓ {name}: {skill.description}")
            
        return "\n".join(capabilities)
        
    def clear(self):
        """Clears the registry (useful for testing)."""
        self.skills.clear()
