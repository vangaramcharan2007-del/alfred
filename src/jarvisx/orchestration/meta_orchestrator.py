"""
Meta-Orchestrator — Dynamic Agentic Scaling Engine.
Analyzes a task and dynamically provisions a bespoke team of agents,
wiring their communication channels (Pub/Sub) on the fly.

Phase 13: THE CODER SWARM — Actually executes tasks via AgentWorker to write files.
"""
import logging
import os
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MetaOrchestrator:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def _push_to_ui(self, event_type: str, data: dict):
        """Broadcast events to E.V. UI."""
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def _analyze_requirements(self, task: str) -> List[str]:
        """Use simple heuristics to determine the required agent roles for a task."""
        logger.info(f"[Orchestrator] Analyzing task complexity: '{task}'")
        self._push_to_ui("swarm_event", {"agent": "Meta-Orchestrator", "action": "Analyzing task complexity..."})
        
        lower_task = task.lower()
        if "database" in lower_task or "sql" in lower_task:
            return ["DBA_Agent", "Backend_Agent"]
        elif "deploy" in lower_task:
            return ["DevOps_Agent"]
        elif "ui" in lower_task or "html" in lower_task:
            return ["Frontend_Agent"]
        else:
            return ["Generalist_Agent"]

    def _get_agent_persona(self, role: str) -> str:
        """Injects a highly rigid system prompt to fine-tune the dynamically spawned agent."""
        personas = {
            "DBA_Agent": "You are a senior Database Architect. You only write hyper-optimized SQL and schema migrations. You despise ORM overhead. No fluff.",
            "DevOps_Agent": "You are a strict DevOps engineer. You focus entirely on Docker, CI/CD pipelines, and zero-downtime deployments.",
            "Security_Auditor": "You are a ruthless Red Team QA reviewer. You actively look for edge cases, memory leaks, and injection flaws.",
            "Generalist_Agent": "You are a 10x Staff Engineer. You write clean, modular, and extremely performant Python code. You do not leave comments unless necessary.",
            "Frontend_Agent": "You are a Senior UI/UX Engineer. You write clean HTML, CSS, and JS. You focus on sleek, cyberpunk/sci-fi aesthetics."
        }
        return personas.get(role, "You are a highly skilled autonomous AI agent focused on executing the user's intent.")

    def orchestrate_task(self, task: str) -> Dict[str, Any]:
        """Dynamically spin up agents, execute, and teardown."""
        roles = self._analyze_requirements(task)
        logger.info(f"[Orchestrator] Provisioning dynamic swarm: {roles}")
        
        from jarvisx.orchestration.agent_worker import AgentWorker
        
        # We'll run the task in the current working directory
        cwd = os.getcwd()
        
        team_logs = []
        all_written_files = []
        
        for role in roles:
            persona = self._get_agent_persona(role)
            logger.info(f"[Orchestrator] Booting {role}... [Persona: {persona[:40]}...]")
            self._push_to_ui("swarm_event", {"agent": "Meta-Orchestrator", "action": f"Provisioned {role}"})
            
            worker = AgentWorker(role=role, persona_prompt=persona)
            result = worker.execute_task(task, workspace_dir=cwd)
            
            if result.get("status") == "success":
                files = result.get("files", [])
                all_written_files.extend(files)
                team_logs.append(f"{role} succeeded. Wrote {len(files)} files.")
            else:
                team_logs.append(f"{role} failed: {result.get('error')}")
            
        logger.info("[Orchestrator] Task complete. Tearing down dynamic swarm.")
        self._push_to_ui("swarm_event", {"agent": "Meta-Orchestrator", "action": "Swarm Teardown Complete."})
        
        return {
            "status": "success",
            "task": task,
            "agents_provisioned": roles,
            "files_written": all_written_files,
            "execution_logs": team_logs
        }
