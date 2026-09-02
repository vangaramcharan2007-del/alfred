import os
import json
import logging
import aiohttp
from typing import Dict, Any, AsyncGenerator

logger = logging.getLogger(__name__)

class OmniRouterClient:
    """
    Central LLM Router for Jarvis X.
    Routes requests through the official OmniRoute gateway.
    Handles fallback to Local Ollama if OmniRoute is unavailable.
    """
    
    def __init__(self):
        self.host = os.getenv("OMNIROUTE_HOST", "127.0.0.1")
        self.port = int(os.getenv("OMNIROUTE_PORT", "20128"))
        self.api_key = os.getenv("OMNIROUTE_API_KEY", "sk-omniroute")
        self.base_url = f"http://{self.host}:{self.port}/v1"
        self.default_model = os.getenv("DEFAULT_MODEL", "llama3")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "llama3")
        
        # Local Ollama fallback URL
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/api")
        self._session = None
        
    def _build_headers(self, context: Dict[str, Any] = None) -> Dict[str, str]:
        """Builds standard HTTP headers for OmniRoute, injecting Jarvis X context."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "JarvisX-Router/1.0"
        }
        
        if context:
            # Pass Jarvis X context as custom headers so OmniRoute can log/route intelligently
            # without exposing private memory to the LLM context.
            if "agent" in context:
                headers["X-Jarvis-Agent"] = context["agent"]
            if "task_type" in context:
                headers["X-Jarvis-Task-Type"] = context["task_type"]
            if "priority" in context:
                headers["X-Jarvis-Priority"] = context["priority"]
            if "capability" in context:
                headers["X-Jarvis-Capability"] = context["capability"]
                
        return headers

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def chat(self, messages: list, model: str = None, context: Dict[str, Any] = None) -> str:
        """Async chat generation."""
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False
        }
        
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=self._build_headers(context),
                json=payload,
                timeout=60
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"OmniRoute error {response.status}. Falling back to Ollama.")
                    return await self._fallback_ollama(messages, target_model)
        except Exception as e:
            logger.error(f"OmniRoute connection failed: {e}. Falling back to Ollama.")
            return await self._fallback_ollama(messages, target_model)

    async def stream_chat(self, messages: list, model: str = None, context: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
        """Async streaming chat generation for voice and live UI."""
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": True
        }
        
        try:
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=self._build_headers(context),
                json=payload
            ) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if line.startswith("data: ") and line != "data: [DONE]":
                                try:
                                    chunk = json.loads(line[6:])
                                    delta = chunk["choices"][0]["delta"]
                                    if "content" in delta:
                                        yield delta["content"]
                                except json.JSONDecodeError:
                                    continue
                    else:
                        logger.warning(f"OmniRoute stream error {response.status}. Falling back to Ollama.")
                        async for chunk in self._fallback_ollama_stream(messages, target_model):
                            yield chunk
        except Exception as e:
            logger.error(f"OmniRoute connection failed: {e}. Falling back to Ollama stream.")
            async for chunk in self._fallback_ollama_stream(messages, target_model):
                yield chunk

    async def _fallback_ollama(self, messages: list, model: str) -> str:
        """Direct fallback to local Ollama API."""
        payload = {
            "model": self.fallback_model,
            "messages": messages,
            "stream": False
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.ollama_base_url}/chat", json=payload, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama fallback failed: {error_text}")
                        return "Error: LLM Gateway and Local Fallback both failed."
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return "Error: Cannot reach local Ollama fallback."

    async def _fallback_ollama_stream(self, messages: list, model: str) -> AsyncGenerator[str, None]:
        """Direct stream fallback to local Ollama API."""
        payload = {
            "model": self.fallback_model,
            "messages": messages,
            "stream": True
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.ollama_base_url}/chat", json=payload) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                try:
                                    chunk = json.loads(line.decode('utf-8'))
                                    if "message" in chunk and "content" in chunk["message"]:
                                        yield chunk["message"]["content"]
                                except json.JSONDecodeError:
                                    continue
                    else:
                        yield "Error: Local fallback failed."
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            yield "Error: Cannot reach local Ollama fallback."

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
            system_prompt += f"\nAvailable Agents:\n" + "\n".join(agent_details)

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
