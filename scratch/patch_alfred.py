import re
import os

with open("src/jarvisx/agents/alfred.py", "r", encoding="utf-8") as f:
    content = f.read()

# Import CapabilityRegistry
if "from jarvisx.agents.capability_registry import CapabilityRegistry" not in content:
    content = content.replace(
        "from jarvisx.agents.registry import AgentRegistry",
        "from jarvisx.agents.registry import AgentRegistry\nfrom jarvisx.agents.capability_registry import CapabilityRegistry"
    )

# Add capability registry to init
if "self.capability_registry = CapabilityRegistry(" not in content:
    content = content.replace(
        "self.registry = registry or AgentRegistry()",
        "self.registry = registry or AgentRegistry()\n        self.capability_registry = CapabilityRegistry(logger=self.logger)"
    )

# Import memory and mission tools if not present
if "from jarvisx.tools.memory import LocalMemoryTool" not in content:
    content = content.replace(
        "from jarvisx.tools.device import SUPPORTED_DEVICE_ACTIONS",
        "from jarvisx.tools.device import SUPPORTED_DEVICE_ACTIONS\nfrom jarvisx.tools.memory import LocalMemoryTool\nfrom jarvisx.tools.missions import MissionTool"
    )

# Add memory and mission tools to init
if "self.memory_tool = LocalMemoryTool" not in content:
    content = content.replace(
        "self.capability_registry = CapabilityRegistry(logger=self.logger)",
        "self.capability_registry = CapabilityRegistry(logger=self.logger)\n        self.memory_tool = LocalMemoryTool(logger=self.logger)\n        self.mission_tool = MissionTool(logger=self.logger)"
    )

# Replace the OmniRouter routing block
old_routing = '''        # OmniRouter multi-agent extraction
        from jarvisx.core.llm_router import OmniRouterClient
        router = OmniRouterClient()
        available_agents = list(self.registry._agents.keys())
        prompt = f"""
You are the Alfred Orchestrator routing engine.
Available agents: {available_agents}
User prompt: "{message}"

Identify which agents are needed to fulfill this prompt. If multiple agents are needed for sequential tasks, list them in order. 
Output ONLY a valid JSON array of strings matching the agent IDs, e.g. ["friday", "edith"]. If you should handle it yourself, return ["alfred"].
"""
        target_agents_json = await router.chat([{"role": "user", "content": prompt}], model="llama3")
        try:
            target_agents = json.loads(target_agents_json)
            if not isinstance(target_agents, list):
                target_agents = [intent.agent_id]  # fallback
        except Exception:
            self.logger.write("error", "alfred.routing.parse_failed", json=target_agents_json)
            target_agents = [intent.agent_id]'''

new_routing = '''        # OmniRouter multi-agent extraction with Capability-Based Intelligence
        from jarvisx.core.llm_router import OmniRouterClient
        router = OmniRouterClient()
        
        # Build memory context
        mem_context = {}
        try:
            active_missions = self.mission_tool.list_active_missions().data
            mem_context["active_missions"] = active_missions
            recent_memories = self.memory_tool.list_memories(category="project", limit=2).data
            mem_context["recent_projects"] = recent_memories
        except Exception as e:
            self.logger.write("warning", "alfred.memory_fetch_failed", error=str(e))
            
        routing_context = {"memory": mem_context}
        
        route_data = await router.route_task(message, context=routing_context, registry=self.capability_registry)
        
        target_agents = [a["name"] for a in route_data.get("selected_agents", [])]
        if not target_agents:
            target_agents = ["alfred"]
'''

if "route_task" not in content:
    content = content.replace(old_routing, new_routing)

with open("src/jarvisx/agents/alfred.py", "w", encoding="utf-8") as f:
    f.write(content)
