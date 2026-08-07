"""Dynamic Skill Loader for Phase 92 Autonomous Skill Acquisition."""

from __future__ import annotations
import importlib.util
import time
from pathlib import Path
from typing import Any, Optional
from jarvisx.agents.action_models import Capability, RiskLevel
from jarvisx.skills.models import SkillMetadata


class SkillLoader:
    """Loads validated Python skill files from disk into executable Capability objects."""

    def load_capability(self, metadata: SkillMetadata) -> Optional[Capability]:
        """Convert a validated SkillMetadata record into an active Capability."""
        p = Path(metadata.file_path)
        if not p.exists():
            return None

        module_name = f"installed_{metadata.name}_{int(time.time())}"
        spec = importlib.util.spec_from_file_location(module_name, str(p))
        if not spec or not spec.loader:
            return None

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Look for Capability class
        inst = None
        for attr in dir(mod):
            if attr.endswith("Capability") and not attr.startswith("_"):
                cls = getattr(mod, attr)
                inst = cls()
                break

        if not inst and hasattr(mod, "execute"):
            handler_fn = mod.execute
        elif inst and hasattr(inst, "execute"):
            handler_fn = inst.execute
        else:
            return None

        return Capability(
            name=metadata.name,
            description=metadata.description,
            category=metadata.category,
            inputs=metadata.inputs,
            risk_level=RiskLevel.LOW,
            permissions=["filesystem_write", "skill_execution"],
            handler=handler_fn
        )
