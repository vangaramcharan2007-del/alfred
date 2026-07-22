from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseSkill(ABC):
    """
    Abstract interface for all Native Jarvis X Skills.
    Skills represent higher-level capabilities that orchestrate tools.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the skill."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the skill does."""
        pass
        
    @property
    @abstractmethod
    def required_tools(self) -> List[str]:
        """A list of tool names from the ToolRegistry required by this skill."""
        pass
        
    @property
    def category(self) -> str:
        """Category of the skill (e.g., 'intelligence', 'coding', 'research')."""
        return "general"
        
    @property
    def cost(self) -> str:
        """Execution cost estimate ('low', 'medium', 'high')."""
        return "medium"
        
    @property
    def success_rate(self) -> float:
        """Default success rate of the skill (0.0 to 1.0)."""
        return 1.0
        
    @property
    def tags(self) -> List[str]:
        """Tags for semantic matching."""
        return []
        
    @property
    def required_permissions(self) -> List[str]:
        """Permissions required by this skill."""
        return []
        
    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any] = None) -> str:
        """
        Executes the skill's logic for a given task.
        
        Args:
            task: The specific instruction or task to perform.
            context: Optional dictionary containing memory or tool references.
            
        Returns:
            A string result of the skill's execution.
        """
        pass
