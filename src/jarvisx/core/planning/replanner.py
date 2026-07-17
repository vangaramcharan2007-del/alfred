import json
from typing import List, Dict, Any
from jarvisx.core.providers.provider_router import ProviderRouter

class Replanner:
    """Generates a corrective plan after a task failure."""
    
    def __init__(self, provider_router: ProviderRouter):
        self.router = provider_router

    async def generate_correction(self, objective: str, failed_task: Dict[str, Any], error_msg: str, logs: str = "") -> List[Dict[str, Any]]:
        """Generates a new plan to recover from the failure."""
        
        prompt = f"""You are a Replanner. A failure occurred during execution. Generate a corrective JSON plan to recover.
Original Objective: {objective}
Failed Task: {failed_task.get('description', 'Unknown')}
Error Message: {error_msg}
Execution Logs: {logs}

The corrective plan should contain the steps needed to fix the issue and resume progress.
Each task must have:
- id: A unique string ID (e.g., 'task_1')
- description: What the task does
- tool: The execution tool to use
- method: The specific method to call
- args: A dictionary of arguments for the method
- confidence: Float between 0 and 1
- depends_on: List of task IDs this task depends on

Ensure you output ONLY raw JSON. No markdown wrappers.
"""
        
        response = await self.router.route_with_failover(
            category="planning",
            action="generate",
            prompt=prompt
        )
        
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
            
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to decode LLM response into JSON: {response}") from e
