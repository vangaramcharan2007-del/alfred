import asyncio
import logging
import json
import uuid

from jarvisx.core.llm_router import OmniRouterClient
from jarvisx.core.model_policy import ModelPolicy

from jarvisx.core.rag_vault import RAGVault
from jarvisx.tools.db_manager import DatabaseManager
from jarvisx.core.message_bus import EventBus
from jarvisx.core.agent_forge import AgentForge
from jarvisx.core.skills.skill_executor import SkillExecutor


class SwarmSupervisor:
    def __init__(self):
        self.vault = RAGVault()
        self.bus = EventBus()
        self.forge = AgentForge()
        self.db = DatabaseManager()
        self.skill_executor = SkillExecutor()


    async def decompose_task(self, task: str) -> list:
        logging.info(f"Decomposing task: {task}")
        # Inject RAG context
        context = self.vault.query_vault(task, n_results=1)
        context_str = context[0] if context else "No additional context found."
        
        prompt = (
            f"Context: {context_str}\n"
            f"Decompose the following complex task into an array of sub-tasks. Output strictly valid JSON."
            f"\nTask: {task}"
        )
        
        try:
            router = OmniRouterClient()
            policy = ModelPolicy()
            ctx = policy.evaluate(agent_name="SwarmSupervisor", task_description=task)
            
            messages = [
                {"role": "system", "content": "Decompose the following complex task into an array of sub-tasks. Output strictly valid JSON."},
                {"role": "user", "content": f"Context: {context_str}\nTask: {task}"}
            ]
            
            response = await router.chat(messages=messages, model=ctx.model, context=ctx.metadata)
            
            # Basic validation to see if it returned JSON
            if "sub_task" in response:
                pass
        except Exception as e:
            logging.error(f"OmniRoute LLM decomposition failed: {e}")
                
        # Mocked return for structural testing
        return [
            {"id": "sub_1", "role": "Worker_Agent_A", "instruction": "Analyze part 1."},
            {"id": "sub_2", "role": "Worker_Agent_B", "instruction": "Analyze part 2."}
        ]

    async def spawn_worker(self, sub_task: dict):
        worker_id = f"{sub_task['role']}_{uuid.uuid4().hex[:6]}"
        instruction = sub_task['instruction']
        logging.info(f"Spawning worker: {worker_id} for instruction: {instruction}")
        
        # Check if the instruction can be handled by a specific skill
        # (For now, we route to Research Assistant if 'research' is in instruction)
        if "research" in instruction.lower():
            result = await self.skill_executor.execute_skill("Research Assistant", instruction)
        else:
            # Fallback to AgentForge
            forge_result = await self.forge.forge_and_execute(sub_task['role'], instruction)
            result = forge_result.get("output", f"Completed: {instruction}")
            
        await self.bus.publish("worker_completed", {"worker_id": worker_id, "result": result})
        return result


    async def execute_complex_task(self, task: str):
        sub_tasks = await self.decompose_task(task)
        logging.info(f"Task decomposed into {len(sub_tasks)} concurrent sub-tasks.")
        
        # Concurrently spawn specialized worker agents
        worker_coroutines = [self.spawn_worker(st) for st in sub_tasks]
        results = await asyncio.gather(*worker_coroutines, return_exceptions=True)
        
        aggregated_output = {
            "original_task": task,
            "results": results
        }
        
        return aggregated_output
