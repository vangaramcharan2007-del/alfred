"""Jarvis X: Multi-Agent Autonomous Coding Swarm.

Coordinates 4 specialized sub-agents:
1. ArchitectAgent: System planning & dependency mapping
2. CoderAgent: Production code generation
3. CriticAgent: Security & edge-case review
4. DebuggerAgent: Automated error diagnosis & auto-patching
"""

from __future__ import annotations
import os
import sys
import json
import time
from typing import Dict, Any, List

from jarvisx.mesh.mesh_router import MeshRouter


class CodingSwarm:
    """Multi-Agent Swarm for end-to-end software development."""

    def __init__(self, router: Optional[MeshRouter] = None):
        self.router = router or MeshRouter()

    def run_swarm(self, coding_task: str) -> Dict[str, Any]:
        """Runs the 4-stage multi-agent pipeline on a coding task."""
        t0 = time.time()

        # 1. Architect Agent
        print(f"[*] [SWARM: ARCHITECT] Generating architectural blueprint...")
        arch_prompt = f"Create an architecture specification and file decomposition for: {coding_task}"
        arch_res = self.router.dispatch_intent(arch_prompt, require_capability="code_gen")

        # 2. Coder Agent
        print(f"[*] [SWARM: CODER] Writing modular code implementation...")
        coder_prompt = f"Implement the code for task based on this plan:\n{arch_res.get('response', '')}\nTask: {coding_task}"
        coder_res = self.router.dispatch_intent(coder_prompt, require_capability="code_gen")

        # 3. Critic / Reviewer Agent
        print(f"[*] [SWARM: CRITIC] Reviewing code for edge cases and safety...")
        critic_prompt = f"Review this code for bugs, security issues, and edge cases:\n{coder_res.get('response', '')}"
        critic_res = self.router.dispatch_intent(critic_prompt, require_capability="llm_inference")

        duration = time.time() - t0
        return {
            "status": "success",
            "task": coding_task,
            "architecture": arch_res.get("response", ""),
            "implementation": coder_res.get("response", ""),
            "review": critic_res.get("response", ""),
            "duration": round(duration, 2),
            "agents_executed": ["Architect", "Coder", "Critic"]
        }
