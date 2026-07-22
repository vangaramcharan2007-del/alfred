import logging
from typing import Any, Dict

from jarvisx.core.skills.skill_registry import SkillRegistry
from jarvisx.core.capabilities.registry import SystemCapabilityRegistry

logger = logging.getLogger(__name__)

class SkillExecutor:
    """
    Executes a skill by name, injecting the necessary tools from the ToolRegistry.
    """
    
    def __init__(self):
        self.skill_registry = SkillRegistry()
        self.tool_registry = SystemCapabilityRegistry()

    async def execute_skill(self, skill_name: str, task: str, context: Dict[str, Any] = None) -> str:
        """
        Locates the skill, prepares its required tools, and executes it.
        """
        skill = self.skill_registry.get_skill(skill_name)
        if not skill:
            error_msg = f"Skill '{skill_name}' not found in registry."
            logger.error(error_msg)
            return error_msg
            
        logger.info(f"Executing skill '{skill_name}' for task: {task}")
        
        # Inject the requested tools into the context
        if context is None:
            context = {}
            
        tools_dict = {}
        for tool_name in skill.required_tools:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                tools_dict[tool_name] = tool
            else:
                logger.warning(f"Skill '{skill_name}' requested tool '{tool_name}' which is not in ToolRegistry.")
                
        context["tools"] = tools_dict
        
        try:
            result = await skill.execute(task, context)
            logger.info(f"Skill '{skill_name}' completed execution.")
            return result
        except Exception as e:
            logger.error(f"Error executing skill '{skill_name}': {e}")
            return f"Skill Execution Error: {str(e)}"
