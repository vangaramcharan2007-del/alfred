from typing import List, Dict, Any
from jarvisx.core.skills.skill_registry import SkillRegistry
from jarvisx.core.workforce_db import WorkforceDatabase

class CapabilityContext:
    """
    Provides safe, constrained context about available skills to the Matcher and Ranker.
    Masks private data and irrelevant memory.
    """
    def __init__(self, registry: SkillRegistry, db: WorkforceDatabase):
        self.registry = registry
        self.db = db

    def get_available_skills_metadata(self) -> List[Dict[str, Any]]:
        """Returns metadata for all available skills."""
        skills = self.registry.skills.values()
        metadata_list = []
        
        for skill in skills:
            stats = self.db.get_skill_stats(skill.name)
            
            metadata = {
                "name": skill.name,
                "description": skill.description,
                "category": getattr(skill, 'category', 'general'),
                "tags": getattr(skill, 'tags', []),
                "required_permissions": getattr(skill, 'required_permissions', []),
                "cost": getattr(skill, 'cost', 'medium'),
                # Merge base success rate with historical stats
                "base_success_rate": getattr(skill, 'success_rate', 1.0),
                "historical_success_rate": stats["success_rate"],
                "total_runs": stats["total_runs"],
                "last_used": stats["last_used"]
            }
            metadata_list.append(metadata)
            
        return metadata_list
