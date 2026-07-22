from typing import Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class RoutingContext:
    model: str
    metadata: Dict[str, Any]

class ModelPolicy:
    """
    Evaluates prompts, intents, and agent context within Jarvis X
    to determine the required task category, priority, and capability.
    Does NOT handle API translation or provider selection.
    """
    
    def __init__(self):
        # We can map capabilities to model aliases configured in OmniRoute
        self.capability_map = {
            "reasoning": "reasoning-model", # e.g. maps to GPT-4o or Claude 3.5 Sonnet in OmniRoute
            "fast": "fast-model",           # e.g. maps to Llama-3-70b or Groq
            "vision": "vision-model",       # e.g. maps to GPT-4V or Gemini-1.5-Pro
            "offline": "local-model"        # e.g. maps to Ollama
        }

    def evaluate(self, agent_name: str, task_description: str, requires_vision: bool = False, is_offline: bool = False) -> RoutingContext:
        """
        Determines the abstract routing requirements.
        """
        if is_offline:
            capability = "offline"
            priority = "high"
        elif requires_vision:
            capability = "vision"
            priority = "normal"
        elif "code" in task_description.lower() or "debug" in task_description.lower() or "analyze" in task_description.lower():
            capability = "reasoning"
            priority = "high"
        else:
            capability = "fast"
            priority = "low"
            
        task_type = "coding" if capability == "reasoning" else "general"
            
        # The model alias that OmniRoute will resolve
        model_alias = self.capability_map.get(capability, "fast-model")
        
        metadata = {
            "agent": agent_name,
            "task_type": task_type,
            "priority": priority,
            "capability": capability
        }
        
        return RoutingContext(model=model_alias, metadata=metadata)
