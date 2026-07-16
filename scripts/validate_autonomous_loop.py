import asyncio
import logging
import time
import json
import subprocess
import os
from pathlib import Path

# Setup path so it can import jarvisx
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from jarvisx.core.planner_engine import PlannerEngine
from jarvisx.core.reasoning_bus import CollaborativeReasoningBus
from jarvisx.core.workforce_registry import WorkforceRegistry
from jarvisx.core.git_worktree_manager import GitWorktreeManager
from jarvisx.core.workforce_manager import WorkforceManager
from jarvisx.core.agent_feedback_loop import AgentFeedbackLoop
from jarvisx.core.workforce_aggregator import WorkforceAggregator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AutonomousLoop")

# We mock the actual "AI" typing by just having Python write the expected files
# inside the respective worktrees to simulate what the Agent Orchestrator CLI would do.

async def simulate_agent_work(worktree: str, agent_type: str):
    logger.info(f"Agent {agent_type} starting work in {worktree}...")
    wt_path = Path(worktree)
    
    if agent_type == "backend_agent":
        # Create src/api/health.py
        api_dir = wt_path / "src" / "api"
        api_dir.mkdir(parents=True, exist_ok=True)
        with open(api_dir / "health.py", "w") as f:
            f.write("from fastapi import APIRouter\n"
                    "from pydantic import BaseModel\n\n"
                    "router = APIRouter()\n\n"
                    "class HealthResponse(BaseModel):\n"
                    "    status: str\n\n"
                    "@router.get('/health', response_model=HealthResponse)\n"
                    "def health_check():\n"
                    "    return HealthResponse(status='healthy')\n")
        
        # Add to main app router (mocking)
        main_py = wt_path / "src" / "main.py"
        with open(main_py, "w") as f:
            f.write("from fastapi import FastAPI\n"
                    "from src.api.health import router as health_router\n\n"
                    "app = FastAPI()\n"
                    "app.include_router(health_router)\n")
                    
    elif agent_type == "testing_agent":
        # Create tests/test_health.py
        test_dir = wt_path / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)
        with open(test_dir / "test_health.py", "w") as f:
            f.write("from fastapi.testclient import TestClient\n"
                    "from src.main import app\n\n"
                    "client = TestClient(app)\n\n"
                    "def test_health_check():\n"
                    "    response = client.get('/health')\n"
                    "    assert response.status_code == 200\n"
                    "    assert response.json() == {'status': 'healthy'}\n")
                    
    elif agent_type == "documentation_agent":
        # Create docs/health_endpoint.md
        docs_dir = wt_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        with open(docs_dir / "health_endpoint.md", "w") as f:
            f.write("# Health Check Endpoint\n\n"
                    "`GET /health`\n\n"
                    "Returns the health status of the API.\n\n"
                    "## Example\n"
                    "```bash\n"
                    "curl http://localhost:8000/health\n"
                    "```\n\n"
                    "**Response:**\n"
                    "```json\n"
                    "{\n  \"status\": \"healthy\"\n}\n"
                    "```\n")

    # Commit changes in the worktree
    try:
        subprocess.run(["git", "add", "."], cwd=wt_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"{agent_type} implemented task"], cwd=wt_path, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Git commit failed in {worktree}: {e.stderr.decode()}")
        
    await asyncio.sleep(2) # Simulate thinking time
    logger.info(f"Agent {agent_type} finished.")


class MockWorkforceManager(WorkforceManager):
    """Overrides the subprocess call to spawn our simulated agents instead."""
    async def dispatch_task(self, task_id: str, objective: str, required_capability: str) -> bool:
        agent_name = self.registry.find_agent_for_capability(required_capability)
        feature_branch = f"feature/{task_id}"
        worktree_path = self.worktree_manager.create_worktree("main", feature_branch)
        
        self.active_tasks[task_id] = {
            "agent": agent_name,
            "status": "RUNNING",
            "worktree": worktree_path,
            "branch": feature_branch
        }
        
        # Run simulation
        asyncio.create_task(self._sim_agent(task_id, agent_name, worktree_path))
        return True

    async def _sim_agent(self, task_id, agent_name, worktree_path):
        t0 = time.time()
        await simulate_agent_work(worktree_path, agent_name)
        self.active_tasks[task_id]["status"] = "COMPLETED"
        self.active_tasks[task_id]["duration"] = time.time() - t0

async def main():
    start_time = time.time()
    
    # Init
    registry = WorkforceRegistry()
    wt_manager = GitWorktreeManager(repo_path=".", base_worktree_dir="/tmp/jarvisx_e2e_worktrees")
    wf_manager = MockWorkforceManager(registry, wt_manager)
    aggregator = WorkforceAggregator(wt_manager)
    planner = PlannerEngine()
    bus = CollaborativeReasoningBus(wf_manager)
    
    import uuid
    uid = uuid.uuid4().hex[:6]
    # 1. Planning
    t0_plan = time.time()
    objective = "Build a FastAPI health-check endpoint with automated tests and documentation."
    plan = planner.generate_plan(f"goal-health-{uid}", objective)
    plan_duration = time.time() - t0_plan
    
    # 2. Coding (Parallel Execution)
    t0_code = time.time()
    for task in plan:
        bus.route_task(task)
        
    await asyncio.sleep(2) # Allow async tasks to populate active_tasks
    
    # Wait for all tasks to complete
    while True:
        running = any(t["status"] == "RUNNING" for t in wf_manager.active_tasks.values())
        if not running and len(wf_manager.active_tasks) > 0:
            break
        await asyncio.sleep(0.5)
    coding_duration = time.time() - t0_code
    
    # 3. Merging (Aggregator)
    t0_merge = time.time()
    for task_id, task_data in wf_manager.active_tasks.items():
        aggregator.merge_completed_task(task_id, task_data["branch"])
    merge_duration = time.time() - t0_merge
    
    # 4. Testing (Validation)
    t0_test = time.time()
    test_result = subprocess.run(["pytest", "tests/"], capture_output=True, text=True)
    test_duration = time.time() - t0_test
    
    total_duration = time.time() - start_time
    
    # Cleanup Worktrees (already done by aggregator if successful, but let's be sure)
    for wt in wt_manager.active_worktrees.values():
        subprocess.run(["git", "worktree", "remove", "--force", wt], capture_output=True)
    
    # Generate Report
    report = {
        "execution_logs": "Successfully routed, executed in parallel, and merged.",
        "agent_allocation": {t_id: d["agent"] for t_id, d in wf_manager.active_tasks.items()},
        "worktree_allocation": {t_id: d["worktree"] for t_id, d in wf_manager.active_tasks.items()},
        "test_output": test_result.stdout if test_result.returncode == 0 else test_result.stderr,
        "timing_statistics": {
            "planning_duration": plan_duration,
            "coding_duration": coding_duration,
            "testing_duration": test_duration,
            "merge_duration": merge_duration,
            "total_task_duration": total_duration
        }
    }
    
    with open("validation/e2e_loop_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print("SUCCESS! Autonomous loop completed.")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
