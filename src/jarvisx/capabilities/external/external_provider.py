from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class Provider(ABC):
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.is_connected = False

    @abstractmethod
    async def connect(self) -> bool:
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def execute(self, action: str, **kwargs) -> Any:
        pass

    @abstractmethod
    def capabilities(self) -> List[str]:
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        pass


class OllamaProvider(Provider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="ollama", config=config)

    async def connect(self) -> bool:
        self.is_connected = True
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        return {"status": "HEALTHY" if self.is_connected else "DISCONNECTED", "provider": "ollama"}

    async def execute(self, action: str, **kwargs) -> Any:
        return {"provider": "ollama", "action": action, "output": f"Ollama model output for {kwargs}"}

    def capabilities(self) -> List[str]:
        return ["chat", "generate", "embeddings", "code_completion"]

    def metadata(self) -> Dict[str, Any]:
        return {"name": "Ollama", "type": "local_llm", "version": "0.3.0"}


class LiteLLMProvider(Provider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="litellm", config=config)

    async def connect(self) -> bool:
        self.is_connected = True
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        return {"status": "HEALTHY" if self.is_connected else "DISCONNECTED", "provider": "litellm"}

    async def execute(self, action: str, **kwargs) -> Any:
        return {"provider": "litellm", "action": action, "output": f"LiteLLM completion for {kwargs}"}

    def capabilities(self) -> List[str]:
        return ["completion", "router", "load_balance"]

    def metadata(self) -> Dict[str, Any]:
        return {"name": "LiteLLM", "type": "llm_router", "version": "1.0.0"}


class OpenRouterProvider(Provider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="openrouter", config=config)

    async def connect(self) -> bool:
        self.is_connected = True
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        return {"status": "HEALTHY" if self.is_connected else "DISCONNECTED", "provider": "openrouter"}

    async def execute(self, action: str, **kwargs) -> Any:
        return {"provider": "openrouter", "action": action, "output": f"OpenRouter response for {kwargs}"}

    def capabilities(self) -> List[str]:
        return ["multi_model_chat", "model_fallback"]

    def metadata(self) -> Dict[str, Any]:
        return {"name": "OpenRouter", "type": "cloud_gateway", "version": "1.0.0"}


class GooseProvider(Provider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="goose", config=config)

    async def connect(self) -> bool:
        self.is_connected = True
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        return {"status": "HEALTHY" if self.is_connected else "DISCONNECTED", "provider": "goose"}

    async def execute(self, action: str, **kwargs) -> Any:
        return {"provider": "goose", "action": action, "output": f"Goose agent execution for {kwargs}"}

    def capabilities(self) -> List[str]:
        return ["autonomous_coding", "refactoring", "tool_calling"]

    def metadata(self) -> Dict[str, Any]:
        return {"name": "Goose", "type": "agent_framework", "version": "1.0.0"}


class OpenHandsProvider(Provider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="openhands", config=config)

    async def connect(self) -> bool:
        self.is_connected = True
        return True

    async def disconnect(self) -> bool:
        self.is_connected = False
        return True

    async def health(self) -> Dict[str, Any]:
        return {"status": "HEALTHY" if self.is_connected else "DISCONNECTED", "provider": "openhands"}

    async def execute(self, action: str, **kwargs) -> Any:
        return {"provider": "openhands", "action": action, "output": f"OpenHands execution for {kwargs}"}

    def capabilities(self) -> List[str]:
        return ["software_engineering", "sandbox_editing", "bash_execution"]

    def metadata(self) -> Dict[str, Any]:
        return {"name": "OpenHands", "type": "ai_engineer", "version": "0.10.0"}
