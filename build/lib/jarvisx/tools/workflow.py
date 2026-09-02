from jarvisx.tools.base import BaseTool, ToolResult
from jarvisx.core.workflows import WorkflowEngine

class WorkflowTool(BaseTool):
    """Tool for querying workflow status."""
    
    def __init__(self, engine: WorkflowEngine):
        self.engine = engine

    def get_status(self, workflow_id: str) -> ToolResult:
        """Check the status of a running workflow."""
        workflow = self.engine.get_workflow(workflow_id)
        if not workflow:
            return ToolResult(success=False, message=f"Workflow {workflow_id} not found.")
            
        return ToolResult(
            success=True,
            data={
                "id": workflow.id,
                "name": workflow.name,
                "state": workflow.state.value,
                "current_step": workflow.current_step_index,
                "error": workflow.error,
                "context": workflow.context
            }
        )
