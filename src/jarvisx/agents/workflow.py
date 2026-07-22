import json
from typing import Optional, Dict, Any

from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event
from jarvisx.tools.workflow import WorkflowTool
from jarvisx.core.workflows.workflow_manager import WorkflowManager, Workflow, WorkflowStep


class WorkflowAgent(BaseAgent):
    """Agent that builds and triggers complex asynchronous workflows."""
    agent_id = "workflow"

    def __init__(self, engine: WorkflowEngine):
        super().__init__()
        self.engine = engine
        self.workflow_tool = WorkflowTool(engine)

    async def handle(self, event: Event) -> AgentResponse:
        from typing import Mapping
        intent_payload = event.payload.get("intent", {})
        intent_label = intent_payload.get("label", "") if isinstance(intent_payload, dict) else ""
        text = str(event.payload.get("message", "")) if isinstance(event.payload, Mapping) else str(event.payload)
        context = {}
        trace_id = event.trace_id
        
        # In a real system, the LLM would parse the intent into a dynamic DAG.
        # For Genesis Phase 6, we implement hardcoded workflow templates based on keywords.
        
        lower_intent = text.lower()
        
        if "status" in lower_intent or "check" in lower_intent:
            workflow_id = context.get("workflow_id")
            if not workflow_id:
                # Try to extract an ID from the intent if not in context
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

        if "deploy" in lower_intent or "deployment" in lower_intent:
            return self._start_deployment_workflow(event)
            
        if "email" in lower_intent:
            return self._start_email_workflow(event)
            
        if "cad" in lower_intent or "generation" in lower_intent:
            # Re-route long CAD generation to a workflow
            return self._start_cad_workflow(event, text)
            
        return self._response(
            event,
            handled=False,
            message="I can only handle specific workflows: deployment, email, cad, or status checks."
        )

    def _start_deployment_workflow(self, event: Event) -> AgentResponse:
        def step1(ctx): return {"build": "success"}
        def step2(ctx): return {"test": "success"}
        def step3(ctx): return {"deploy": "success"}
        
        workflow = Workflow(
            name="Deployment Workflow",
            context={"trace_id": event.trace_id},
            steps=[
                WorkflowStep("Build", step1),
                WorkflowStep("Test", step2),
                WorkflowStep("Deploy", step3)
            ]
        )
        wid = self.engine.start(workflow)
        return self._response(
            event,
            handled=True,
            message=f"Deployment workflow started asynchronously. (ID: {wid})"
        )

    def _start_email_workflow(self, event: Event) -> AgentResponse:
        def step1(ctx): return {"draft": "Drafted email."}
        def step2(ctx): return {"send": "Sent email."}
        
        workflow = Workflow(
            name="Email Workflow",
            context={"trace_id": event.trace_id},
            steps=[
                WorkflowStep("Draft", step1),
                WorkflowStep("Send", step2)
            ]
        )
        wid = self.engine.start(workflow)
        return self._response(
            event,
            handled=True,
            message=f"Email workflow started asynchronously. (ID: {wid})"
        )

    def _start_cad_workflow(self, event: Event, prompt: str) -> AgentResponse:
        def generate_step(ctx): 
            # In a real impl, this would call CADTool.
            import time
            time.sleep(0.5) # Simulate long task
            return {"file": "output.scad"}
            
        workflow = Workflow(
            name="CAD Generation Workflow",
            context={"trace_id": event.trace_id, "prompt": prompt},
            steps=[
                WorkflowStep("Generate SCAD", generate_step)
            ]
        )
        wid = self.engine.start(workflow)
        return self._response(
            event,
            handled=True,
            message=f"CAD generation started asynchronously in the background. (ID: {wid})"
        )
