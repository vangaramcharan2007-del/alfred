"""Autonomous Skill Synthesizer Agent (Layer 3 - Agent Layer).

Observes workflows and distills recurring problem-solving patterns into reusable skills and capabilities.
"""

from typing import Any, Dict, Optional
from jarvisx.agents.base import OperationalAgent
from jarvisx.automation.skill_synthesis import SkillSynthesisEngine


class SynthesizerAgent(OperationalAgent):
    """Specialized worker for autonomous skill distillation and capability generation."""

    __test__ = False

    def __init__(self, name: str = "synthesizer_agent", engine: Optional[SkillSynthesisEngine] = None):
        super().__init__(
            name=name,
            purpose="Autonomous workflow pattern analysis, SKILL.md synthesis, and runtime tool generation",
            capabilities=["workflow_distillation", "skill_synthesis", "capability_registration"],
            permissions=["read_filesystem", "write_skill_catalog", "register_tools"],
            hspw_multiplier=2.5,
        )
        self.engine = engine or SkillSynthesisEngine()

    def _execute_task(self, task: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        action = task.get("action", "status")

        if action in ("distill", "synthesize", "create_skill", "skill"):
            res = self.engine.distill_workflow(
                name=task.get("name", "Custom Workflow"),
                description=task.get("description", "Autonomously synthesized reusable capability"),
                steps=task.get("steps", ["Inspect environment", "Validate preconditions", "Execute automated task"]),
                parameters=task.get("parameters"),
            )
            self.engine.register_synthesized_capability(res["skill"]["id"], handler_action=f"execute_{res['skill']['id']}")
            return {"status": "completed", "result": res}

        elif action == "status":
            saved = self.metrics()["hours_saved"]
            cat = self.engine.get_catalog_summary()
            output = (
                f"AUTONOMOUS SKILL SYNTHESIS STATUS:\n"
                f"  • Synthesized Skills: {cat['total_skills']} packages\n"
                f"  • Runtime Capabilities: {cat['total_capabilities']} descriptors\n"
                f"  • Synthesis Time Saved: +{saved:.2f} HSPW"
            )
            return {"status": "completed", "output": output, "hspw": saved}

        return {"status": "error", "message": f"Unknown Synthesizer action: {action}"}
