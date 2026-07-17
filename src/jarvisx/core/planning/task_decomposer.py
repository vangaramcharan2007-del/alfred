import json
from typing import List, Dict, Any
from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.providers.fallback_manager import FallbackManager

class TaskDecomposer:
    """Converts objectives into actionable tasks by querying the LLM provider."""
    
    def __init__(self, provider_router: ProviderRouter):
        self.router = provider_router

    async def decompose(self, objective: str, context: str = "") -> List[Dict[str, Any]]:
        """Breaks down an objective into a JSON plan."""
        
        prompt = f"""You are a Task Decomposer. Break down the following objective into a JSON array of tasks.
Objective: {objective}
Context: {context}

Each task must have:
- id: A unique string ID (e.g., 'task_1')
- description: What the task does
- tool: The execution tool to use (e.g., 'file_ops', 'command_executor')
- method: The specific method to call on the tool (e.g., 'create_file', 'execute')
- args: A dictionary of arguments for the method (e.g., {{"filepath": "hello.py", "content": "print('hello')"}})
- confidence: Float between 0 and 1
- depends_on: List of task IDs this task depends on

Ensure you output ONLY raw JSON. No markdown wrappers.
Example:
[
  {{
    "id": "task_1",
    "description": "Create hello.py",
    "tool": "file_ops",
    "method": "create_file",
    "args": {{"filepath": "hello.py", "content": "print('Hello World')"}},
    "confidence": 0.99,
    "depends_on": []
  }}
]
"""
        
        # Route to provider without tying to a specific SDK
        response = await self.router.route_with_failover(
            category="planning",
            action="generate",
            prompt=prompt
        )
        
        # Clean response (remove simulated brackets if any, or markdown formatting)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
            
        try:
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to decode LLM response into JSON: {response}") from e
