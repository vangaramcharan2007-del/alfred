"""
Coder Swarm — Multi-Agent Coding Workspace.
Spawns specialized agents (Planner, Frontend, Backend, QA) to build apps.
"""
import asyncio
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CoderSwarm:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    async def build_app(self, requirements: str) -> Dict[str, Any]:
        """Orchestrate 4 agents to build a requested app."""
        import ollama
        
        # 1. Planner
        plan_res = ollama.chat(model="qwen2.5-coder:1.5b", messages=[
            {"role": "system", "content": "You are a software architect. Break this into frontend and backend tasks."},
            {"role": "user", "content": requirements}
        ])
        plan = plan_res["message"]["content"]
        
        # 2. Parallel Coding
        async def code_frontend():
            return ollama.chat(model="qwen2.5-coder:1.5b", messages=[
                {"role": "system", "content": "You are a Frontend dev. Write the UI code for this plan."},
                {"role": "user", "content": plan}
            ])["message"]["content"]
            
        async def code_backend():
            return ollama.chat(model="qwen2.5-coder:1.5b", messages=[
                {"role": "system", "content": "You are a Backend dev. Write the server code for this plan."},
                {"role": "user", "content": plan}
            ])["message"]["content"]
            
        frontend, backend = await asyncio.gather(code_frontend(), code_backend())
        
        # 3. QA
        qa_res = ollama.chat(model="qwen2.5-coder:1.5b", messages=[
            {"role": "system", "content": "You are a QA Tester. Review this code and give a final approval summary."},
            {"role": "user", "content": f"Frontend:\n{frontend}\n\nBackend:\n{backend}"}
        ])
        qa = qa_res["message"]["content"]
        
        return {
            "status": "success",
            "plan": plan,
            "frontend_code": frontend,
            "backend_code": backend,
            "qa_report": qa
        }
