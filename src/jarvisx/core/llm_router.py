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

    async def chat(self, messages: list, model: str = None, context: Dict[str, Any] = None) -> str:
        """Standard async non-streaming chat generation."""
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
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
            async with aiohttp.ClientSession() as session:
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
