import os
import uuid
import asyncio
import logging
from jarvisx.tools.sandbox_exec import RuntimeSandbox

class AgentForge:
    def __init__(self, agents_dir: str = "src/jarvisx/agents/"):
        self.agents_dir = agents_dir
        os.makedirs(self.agents_dir, exist_ok=True)
        self.sandbox = RuntimeSandbox(timeout_seconds=30)

    def _generate_agent_code(self, role: str, task: str) -> str:
        return f"""
import asyncio
import sys
import psutil
import time

try:
    from jarvisx.core.llm_router import OmniRouterClient
    from jarvisx.core.model_policy import ModelPolicy
except ImportError:
    OmniRouterClient = None

async def main():
    if "{role}" == "Diagnostic Agent":
        import datetime
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        result = "OS Boot Time: " + boot_time
    else:
        if OmniRouterClient:
            try:
                router = OmniRouterClient()
                policy = ModelPolicy()
                ctx = policy.evaluate(agent_name="{role}", task_description="{task}")
                
                messages = [
                    {{"role": "system", "content": "You are a {role}."}},
                    {{"role": "user", "content": "{task}"}}
                ]
                result = await router.chat(messages=messages, model=ctx.model, context=ctx.metadata)
            except Exception as e:
                result = f"OmniRoute Error: {{e}}"
        else:
            result = "OmniRouterClient not available in sandbox."

    print(f"AGENT_RESULT: {{result}}")

if __name__ == "__main__":
    asyncio.run(main())
"""

    async def forge_and_execute(self, role: str, task: str) -> dict:
        code = self._generate_agent_code(role, task)
        agent_id = str(uuid.uuid4())[:8]
        agent_path = os.path.join(self.agents_dir, f"agent_{agent_id}.py")
        
        try:
            with open(agent_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            with open(agent_path, "r", encoding="utf-8") as f:
                code_content = f.read()
            
            result = self.sandbox.execute_code(code_content)
            
            output = result.get("output", "")
            if "AGENT_RESULT:" in output:
                parsed_result = output.split("AGENT_RESULT:")[1].strip()
                try:
                    from src.jarvisx.core.message_bus import EventBus
                    bus = EventBus()
                    await bus.publish("agent_completed", {"role": role, "result": parsed_result})
                except Exception as e:
                    logging.error(f"Bus error: {{e}}")
            
            return result
        finally:
            if os.path.exists(agent_path):
                os.remove(agent_path)

async def self_test():
    forge = AgentForge()
    res = await forge.forge_and_execute("Diagnostic Agent", "Query OS uptime")
    print("Self-test complete:", res)

if __name__ == "__main__":
    asyncio.run(self_test())
