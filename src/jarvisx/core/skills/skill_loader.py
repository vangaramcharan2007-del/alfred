import os
import importlib.util
import inspect
import logging
from typing import List

from jarvisx.core.skills.skill import BaseSkill
from jarvisx.core.skills.skill_registry import SkillRegistry

logger = logging.getLogger(__name__)

class SkillLoader:
    """
    Dynamically loads Jarvis X skills from a specified directory.
    """
    
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self.registry = SkillRegistry()

    def load_all(self) -> int:
        """
        Scans the directory and loads all valid BaseSkill implementations.
        Returns the number of loaded skills.
        """
        if not os.path.exists(self.skills_dir):
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return 0
            
        loaded_count = 0
        
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                filepath = os.path.join(self.skills_dir, filename)
                module_name = f"jarvisx.core.skills.installed.{filename[:-3]}"
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Find classes that inherit from BaseSkill
                        for _, obj in inspect.getmembers(module, inspect.isclass):
                            if issubclass(obj, BaseSkill) and obj is not BaseSkill:
                                skill_instance = obj()
                                self.registry.register(skill_instance)
                                loaded_count += 1
                except Exception as e:
                    logger.error(f"Failed to load skill from {filename}: {e}")
                    
        return loaded_count
