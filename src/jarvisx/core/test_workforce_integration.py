import asyncio
import logging
import json
from src.jarvisx.core.planner_engine import PlannerEngine
from src.jarvisx.core.reasoning_bus import CollaborativeReasoningBus
from src.jarvisx.core.workforce_registry import WorkforceRegistry
from src.jarvisx.core.git_worktree_manager import GitWorktreeManager
from src.jarvisx.core.workforce_manager import WorkforceManager
from src.jarvisx.core.agent_feedback_loop import AgentFeedbackLoop

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestWorkforceIntegration")

async def run_end_to_end_test():
    logger.info("=== Starting Workforce E2E Validation ===")
    
    # Setup dependencies
    registry = WorkforceRegistry()
    worktree_manager = GitWorktreeManager(repo_path=".", base_worktree_dir="/tmp/jarvisx_tests_worktrees")
    wf_manager = WorkforceManager(registry, worktree_manager)
    feedback_loop = AgentFeedbackLoop(wf_manager, max_retries=3)
    reasoning_bus = CollaborativeReasoningBus(wf_manager)
    planner = PlannerEngine()
    
    # User Command
    objective = "Build authentication system"
    logger.info(f"User Directive: {objective}")
    
    # 1. Plan
    plan = planner.generate_plan("goal-auth-sys", objective)
    logger.info(f"Planner generated: {json.dumps(plan, indent=2)}")
    
    # 2. Route & Execute
    for task in plan:
        reasoning_bus.route_task(task)
        
    await asyncio.sleep(1) # Allow async dispatch to fire
    
    # 3. Simulate Agent Failure Feedback Loop
    failed_task_id = "goal-auth-sys-backend"
    if failed_task_id in wf_manager.active_tasks:
        logger.info("Simulating CI failure on backend agent...")
        wf_manager.active_tasks[failed_task_id]["status"] = "COMPLETED"
        await feedback_loop.handle_task_completion(failed_task_id, {"execution_logs": "Error: Pytest assertion failed on login route."})
        
    await asyncio.sleep(1)
    
    logger.info("=== E2E Validation Complete ===")

if __name__ == "__main__":
    asyncio.run(run_end_to_end_test())
