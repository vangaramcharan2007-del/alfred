import re

with open("src/jarvisx/core/llm_router.py", "r", encoding="utf-8") as f:
    content = f.read()

new_method = '''
    async def route_task(self, message: str, context: Dict[str, Any] = None, registry=None) -> Dict[str, Any]:
        """
        Dynamically route a user prompt using Capability-Based Intelligence.
        Asks the LLM to extract intent and required capabilities, then optionally uses 
        the CapabilityRegistry to select agents if the LLM cannot confidently match them.
        """
        
        system_prompt = """
You are the Jarvis X OmniRouter. Your goal is to route a user's request based on capabilities.

Output ONLY a valid JSON object matching this schema exactly:
{
 "intent": "string (the core intent of the prompt)",
 "required_capabilities": ["string", "string"],
 "selected_agents": [
   {
    "name": "string (agent id)",
    "confidence": float (0.0 to 1.0)
   }
 ]
}
"""
        if registry:
            agent_details = []
            for agent in registry.list_agents():
                agent_details.append(f"- {agent.id}: {agent.role} (capabilities: {', '.join(agent.capabilities)})")
            system_prompt += f"\\nAvailable Agents:\\n" + "\\n".join(agent_details)

        messages = [
            {"role": "system", "content": system_prompt.strip()},
        ]
        
        if context and "memory" in context:
            messages.append({"role": "system", "content": f"Memory Context: {json.dumps(context['memory'])}"})
            
        messages.append({"role": "user", "content": message})

        # Ask the LLM
        response_text = await self.chat(messages, model=self.default_model, context=context)
        
        try:
            # Strip markdown blocks if present
            clean_json = response_text
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].strip()
                
            data = json.loads(clean_json)
            
            # Validation
            if "intent" not in data or "required_capabilities" not in data or "selected_agents" not in data:
                raise ValueError("Missing required keys in LLM output schema.")
                
            # If the LLM didn't pick any agents (or we want to enforce registry ranking),
            # we can augment/replace the selected_agents using the Registry's rank_agents logic.
            if registry and data.get("required_capabilities"):
                discovered = registry.discover_capability(data["required_capabilities"])
                if discovered:
                    # Merge LLM selection with Registry selection (Registry wins)
                    data["selected_agents"] = [{"name": d["agent"], "confidence": d["confidence"]} for d in discovered]

            return data
        except Exception as e:
            logger.error(f"OmniRouter failed to parse capability route: {e}")
            # Fallback to existing routing
            return {
                "intent": "unknown",
                "required_capabilities": [],
                "selected_agents": [{"name": "alfred", "confidence": 1.0}]
            }
'''

if "async def route_task" not in content:
    content += new_method

with open("src/jarvisx/core/llm_router.py", "w", encoding="utf-8") as f:
    f.write(content)
