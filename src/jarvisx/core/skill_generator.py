import os
import json
import time

class SkillGenerator:
    """Owns scaffold creation for new capabilities."""
    
    SKILLS_DIR = "src/jarvisx/skills"
    
    def __init__(self):
        os.makedirs(self.SKILLS_DIR, exist_ok=True)
        
    def _to_camel_case(self, snake_str: str) -> str:
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)
        
    def create_skill(self, capability: str):
        """Create scaffold skill files and metadata files."""
        class_name = f"{self._to_camel_case(capability)}Skill"
        
        # 1. Generate Python Scaffold
        py_path = os.path.join(self.SKILLS_DIR, f"{capability}.py")
        py_code = f"""class {class_name}:
    def execute(self, payload):
        raise NotImplementedError(
            "Generated scaffold created by Jarvis X Evolution Engine."
        )
"""
        with open(py_path, "w") as f:
            f.write(py_code)
            
        print(f"Created:\n{capability}.py\n")
            
        # 2. Generate Metadata
        json_path = os.path.join(self.SKILLS_DIR, f"{capability}.json")
        metadata = {
            "name": capability,
            "generated_by": "capability_evolution_engine",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "version": "0.1",
            "status": "scaffold"
        }
        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Created:\n{capability}.json\n")
