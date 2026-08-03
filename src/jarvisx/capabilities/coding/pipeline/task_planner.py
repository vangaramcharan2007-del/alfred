from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from jarvisx.capabilities.coding.pipeline.repository_analyzer import RepositoryContext, RepositoryProfile
from jarvisx.capabilities.coding.code_graph import CodeGraph
from jarvisx.capabilities.coding.architecture_memory import ArchitectureMemory

@dataclass
class PlanStep:
    step_id: int
    title: str
    description: str
    target_file: Optional[str] = None
    action_type: str = "modify"  # create, modify, test, review

@dataclass
class TaskPlan:
    task_description: str
    repository_context: RepositoryContext
    steps: List[PlanStep] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_description": self.task_description,
            "repository_context": self.repository_context.to_dict(),
            "steps": [
                {
                    "step_id": s.step_id,
                    "title": s.title,
                    "description": s.description,
                    "target_file": s.target_file,
                    "action_type": s.action_type
                }
                for s in self.steps
            ]
        }

class TaskPlanner:
    def plan_task(
        self,
        task_description: str,
        repo_context: RepositoryContext,
        code_graph: Optional[CodeGraph] = None,
        architecture_memory: Optional[ArchitectureMemory] = None
    ) -> TaskPlan:
        steps: List[PlanStep] = []
        desc_lower = task_description.lower()
        profile = repo_context.profile

        # Check existing codebase components in graph
        has_auth_module = False
        if code_graph:
            auth_nodes = code_graph.search("auth")
            has_auth_module = len(auth_nodes) > 0

        if "auth" in desc_lower or "authentication" in desc_lower:
            target_file = "auth.py" if repo_context.primary_language == "python" else "auth.js"
            action = "modify" if has_auth_module or (repo_context.key_files and target_file in repo_context.key_files) else "create"
            
            steps.append(PlanStep(
                step_id=1,
                title="Integrate Auth Schema & Route",
                description=f"{'Extend existing auth module' if has_auth_module else 'Create new auth route'} with JWT token verification",
                target_file=target_file,
                action_type=action
            ))
            steps.append(PlanStep(
                step_id=2,
                title="Connect Auth to Router",
                description="Attach authentication middleware to protected API endpoints",
                target_file="main.py" if repo_context.primary_language == "python" else "index.js",
                action_type="modify"
            ))
            steps.append(PlanStep(
                step_id=3,
                title="Run Auth Tests",
                description="Verify token issuance, verification, and unauthorized access rejections",
                target_file="test_auth.py" if repo_context.primary_language == "python" else "test_auth.js",
                action_type="test"
            ))
        elif "calculator" in desc_lower or "api endpoint" in desc_lower:
            target_file = "main.py" if repo_context.primary_language == "python" else "app.js"
            steps.append(PlanStep(
                step_id=1,
                title="Design API Route",
                description=f"Plan endpoint schema for calculator feature in {target_file}",
                target_file=target_file,
                action_type="create" if not (repo_context.root_path and (target_file in repo_context.key_files)) else "modify"
            ))
            steps.append(PlanStep(
                step_id=2,
                title="Implement Route & Logic",
                description="Write request handling and business logic for addition/subtraction/multiplication/division",
                target_file=target_file,
                action_type="modify"
            ))
            steps.append(PlanStep(
                step_id=3,
                title="Run Unit Tests",
                description="Execute test suite to verify endpoint responses and handle edge cases (e.g. division by zero)",
                target_file="test_main.py" if repo_context.primary_language == "python" else "test.js",
                action_type="test"
            ))
            steps.append(PlanStep(
                step_id=4,
                title="Code & Security Review",
                description="Review patch for safety, validation, and performance standards",
                action_type="review"
            ))
        else:
            steps.append(PlanStep(
                step_id=1,
                title="Analyze Requirements",
                description=f"Deconstruct request '{task_description}' for framework '{repo_context.framework}'",
                action_type="analyze"
            ))
            steps.append(PlanStep(
                step_id=2,
                title="Execute Changes",
                description="Apply code edits to codebase",
                target_file="main.py" if repo_context.primary_language == "python" else "index.js",
                action_type="modify"
            ))
            steps.append(PlanStep(
                step_id=3,
                title="Validate Changes",
                description="Run test suite and review patch",
                action_type="test"
            ))

        return TaskPlan(
            task_description=task_description,
            repository_context=repo_context,
            steps=steps
        )
