import json
from typing import Optional, Dict, Any

from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event
from jarvisx.tools.workflow import WorkflowTool
from jarvisx.core.workflows import WorkflowEngine, Workflow, WorkflowStep


class WorkflowAgent(BaseAgent):
    """Agent that builds and triggers complex asynchronous workflows."""
    agent_id = "workflow"

    def __init__(self, engine: WorkflowEngine):
        super().__init__()
        self.engine = engine
        self.workflow_tool = WorkflowTool(engine)
        
        try:
            from jarvisx.core.llm_router import OmniRouterClient
            self.router = OmniRouterClient()
        except ImportError:
            self.router = None

    async def handle(self, event: Event) -> AgentResponse:
        from typing import Mapping
        import asyncio
        
        intent_payload = event.payload.get("intent", {})
        text = str(event.payload.get("message", "")) if isinstance(event.payload, Mapping) else str(event.payload)
        context = {}
        trace_id = event.trace_id
        
        lower_intent = text.lower()
        
        # Keep status checking intact
        if "status" in lower_intent or "check workflow" in lower_intent:
            parts = text.split()
            workflow_id = parts[-1] if len(parts) > 1 else ""
            res = self.workflow_tool.get_status(workflow_id)
            if res.success:
                return self._response(
                    event,
                    handled=True,
                    message=f"Workflow {workflow_id} is {res.data['state']}.",
                    data=res.data
                )
            return self._response(event, handled=True, message=res.message)

        # Dynamic Workflow Generation
        if not self.router:
            return self._response(
                event,
                handled=False,
                message="Cannot generate workflow: OmniRouterClient is unavailable."
            )
            
        system_prompt = """
You are Jarvis X's Workflow Generator.
Given a user's task, break it down into a sequence of discrete steps.
For each step, generate a valid Python function that takes a `ctx` (dict) argument and returns a dict.
Do not use `time.sleep` in steps; workflows are asynchronous.
Output ONLY a JSON array of objects, with no markdown formatting or backticks.
Format:
[
  {
    "name": "Step Name",
    "code": "def run(ctx):\n    return {'result': 'data'}"
  }
]
"""
        try:
            # Request the LLM to generate the steps
            llm_response = await asyncio.to_thread(
                self.router.generate,
                prompt=text,
                system=system_prompt,
                model="gpt-4"
            )
            
            # Clean response
            llm_text = llm_response.text.strip()
            if llm_text.startswith("```json"):
                llm_text = llm_text[7:]
            if llm_text.startswith("```"):
                llm_text = llm_text[3:]
            if llm_text.endswith("```"):
                llm_text = llm_text[:-3]
                
            steps_data = json.loads(llm_text.strip())
            
            # Build the DAG dynamically
            workflow_steps = []
            for i, step_info in enumerate(steps_data):
                step_name = step_info.get("name", f"Step_{i}")
                code_str = step_info.get("code", "def run(ctx): return {}")
                
                # We dynamically execute the LLM's generated string into a real Python function
                # Note: In a production system, use sandbox_exec.py here for security.
                local_env = {}
                exec(code_str, {}, local_env)
                
                # Find the callable (usually 'run')
                callable_func = next((v for k, v in local_env.items() if callable(v)), None)
                if not callable_func:
                    # Fallback if the LLM didn't write a proper function
                    def dummy(ctx): return {"error": "Invalid code generated"}
                    callable_func = dummy
                    
                workflow_steps.append(WorkflowStep(step_name, callable_func))
                
            workflow = Workflow(
                name=f"Dynamic: {text[:20]}...",
                context={"trace_id": event.trace_id},
                steps=workflow_steps
            )
            
            wid = self.engine.start(workflow)
            return self._response(
                event,
                handled=True,
                message=f"Dynamically generated and started workflow '{workflow.name}'. (ID: {wid})"
            )
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Dynamic workflow generation failed: {e}")
            return self._response(
                event,
                handled=True,
                message=f"Failed to dynamically generate workflow: {e}"
            )
