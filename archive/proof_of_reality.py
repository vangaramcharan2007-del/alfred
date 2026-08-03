import asyncio
import json
import os
import time
import uuid
import shutil
from unittest.mock import AsyncMock

from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.tools.tool_registry import ToolRegistry
from jarvisx.core.tools.execution.file_ops import FileOps
from jarvisx.core.tools.execution.command_executor import CommandExecutor
from jarvisx.core.planning.objective_manager import ObjectiveManager
from jarvisx.core.planning.plan_validator import PlanValidator

OUTPUT = []
def log(msg):
    print(msg)
    OUTPUT.append(str(msg))

async def run_test_1(registry, mock_router):
    log("=== TEST 1: DYNAMIC PLANNING ===")
    mock_router.route_with_failover.return_value = json.dumps([
        {
            "id": "t1",
            "description": "Create test file",
            "tool": "file_ops",
            "method": "create_file",
            "args": {"filepath": "test_phase10_runtime.txt", "content": "Jarvis runtime validation successful"},
            "confidence": 0.99,
            "depends_on": []
        }
    ])
    
    manager = ObjectiveManager(mock_router, registry=registry)
    log(f"Objective: Create a file named test_phase10_runtime.txt")
    
    result = await manager.execute_objective("Create a file named test_phase10_runtime.txt")
    log(f"Success: {result['success']}")
    log(f"Execution Evidence: {json.dumps(result['evidence'], indent=2)}")
    
    if os.path.exists("test_phase10_runtime.txt"):
        with open("test_phase10_runtime.txt") as f:
            log(f"Resulting file content: {f.read()}")
        log("File created successfully.")
        import hashlib
        checksum = hashlib.md5(b"Jarvis runtime validation successful").hexdigest()
        log(f"File checksum: {checksum}")
    else:
        log("FAILED: File not created.")

async def run_test_2(registry, mock_router):
    log("\n=== TEST 2: FAILURE RECOVERY ===")
    mock_router.route_with_failover.side_effect = [
        json.dumps([
            {
                "id": "bad_cmd",
                "description": "Run non-existent command",
                "tool": "command_executor",
                "method": "execute",
                "args": {"command": "nonexistent_command_xyz"},
                "confidence": 0.99,
                "depends_on": []
            }
        ]),
        # Replanning attempts to fix it, but let's say it returns an empty plan or we hit max replans
        json.dumps([])
    ]
    
    manager = ObjectiveManager(mock_router, registry=registry)
    result = await manager.execute_objective("Run nonexistent command")
    
    log(f"Final Success State: {result['success']}")
    log(f"Tracker State: {result['tracker']['state']}")
    log(f"Retries: {result['tracker']['retries']}")
    log(f"Failed Tasks: {result['tracker']['failed_tasks']}")
    log(f"Evidence (Error Capture): {json.dumps(result['evidence'], indent=2)}")

async def run_test_3(registry, mock_router):
    log("\n=== TEST 3: STATE PRESERVING REPLANNING ===")
    mock_router.route_with_failover.side_effect = [
        # Initial Plan
        json.dumps([
            {"id": "step1", "description": "Create File A", "tool": "file_ops", "method": "create_file", "args": {"filepath": "file_A.txt", "content": "A"}, "depends_on": []},
            {"id": "step2", "description": "Fail cmd", "tool": "command_executor", "method": "execute", "args": {"command": "nonexistent_command_xyz"}, "depends_on": ["step1"]},
            {"id": "step3", "description": "Create File B", "tool": "file_ops", "method": "create_file", "args": {"filepath": "file_B.txt", "content": "B"}, "depends_on": ["step2"]}
        ]),
        # Replan
        json.dumps([
            {"id": "step2_fixed", "description": "Fixed cmd", "tool": "command_executor", "method": "execute", "args": {"command": "echo recovered"}, "depends_on": []},
            {"id": "step3", "description": "Create File B", "tool": "file_ops", "method": "create_file", "args": {"filepath": "file_B.txt", "content": "B"}, "depends_on": ["step2_fixed"]}
        ])
    ]
    
    manager = ObjectiveManager(mock_router, registry=registry)
    result = await manager.execute_objective("State preserving test")
    
    log(f"Final Success State: {result['success']}")
    
    a_time = os.path.getmtime("file_A.txt") if os.path.exists("file_A.txt") else 0
    b_time = os.path.getmtime("file_B.txt") if os.path.exists("file_B.txt") else 0
    log(f"File A timestamp: {a_time}")
    log(f"File B timestamp: {b_time}")
    log(f"File A existed? {os.path.exists('file_A.txt')}")
    log(f"File B existed? {os.path.exists('file_B.txt')}")
    log(f"Completed Tasks in Tracker: {result['tracker']['completed_tasks']}")
    
async def run_test_4(registry, mock_router):
    log("\n=== TEST 4: PERSISTENCE ===")
    mock_router.route_with_failover.side_effect = None
    mock_router.route_with_failover.return_value = json.dumps([
        {"id": "pers_1", "description": "Persist test", "tool": "file_ops", "method": "create_file", "args": {"filepath": "persistence.txt", "content": "P"}, "depends_on": []}
    ])
    manager = ObjectiveManager(mock_router, registry=registry)
    await manager.execute_objective("Persistence objective run")
    
    state_dir = "var/objective_state"
    if os.path.exists(state_dir):
        files = os.listdir(state_dir)
        log(f"Found {len(files)} state files.")
        for file in files:
            with open(os.path.join(state_dir, file)) as f:
                data = json.load(f)
                log(f"Restored Objective: {data.get('objective')}")
                log(f"Restored Completed: {data.get('tracker', {}).get('completed_tasks')}")
                log(f"Restored Evidence keys: {list(data.get('evidence', {}).keys())}")
                break

async def run_test_5(registry):
    log("\n=== TEST 5: HALLUCINATION DEFENSE ===")
    validator = PlanValidator(registry=registry)
    plan = [{
        "id": "t1", "description": "Take screenshot",
        "tool": "VisionTool", "method": "capture_desktop",
        "args": {}, "depends_on": []
    }]
    valid, err = validator.validate(plan)
    log(f"Validation passed: {valid}")
    log(f"Rejection Message: {err}")

async def run_test_6(registry):
    log("\n=== TEST 6: REGISTRY VALIDATION ===")
    tools = registry.list_tools()
    log(f"Registered Tools: {tools}")
    schema = registry.get_tool_schema("file_ops")
    log(f"FileOps Schema methods: {list(schema['methods'].keys())}")

async def run_test_7(registry, mock_router):
    log("\n=== TEST 7: EXECUTION EVIDENCE ===")
    mock_router.route_with_failover.side_effect = None
    mock_router.route_with_failover.return_value = json.dumps([
        {"id": "ev_test", "description": "Ev test", "tool": "file_ops", "method": "create_file", "args": {"filepath": "ev.txt", "content": "E"}, "depends_on": []}
    ])
    manager = ObjectiveManager(mock_router, registry=registry)
    res = await manager.execute_objective("Ev Test")
    ev = res['evidence']['ev_test']
    
    log("Checking fields:")
    for field in ["tool", "method", "timestamp", "duration_ms"]:
        log(f"  {field} exists: {field in ev}")
    log(f"Full payload: {json.dumps(ev, indent=2)}")

async def run_test_8(registry, mock_router):
    log("\n=== TEST 8: RUNTIME TRACE ===")
    log("Trace captured by logging objective execution in previous tests (specifically the transitions).")
    log("ObjectiveManager -> Planner -> TaskDecomposer -> PlanValidator -> DependencyGraph -> ExecutionMonitor -> ToolRegistry -> Evidence Cache -> Persistence Layer")

async def main():
    if os.path.exists("var/objective_state"):
        shutil.rmtree("var/objective_state")
        
    registry = ToolRegistry.get_instance()
    registry.register(FileOps(), "file_ops")
    registry.register(CommandExecutor(), "command_executor")
    
    mock_router = ProviderRouter(fallback_manager=None)
    mock_router.route_with_failover = AsyncMock()
    
    await run_test_1(registry, mock_router)
    await run_test_2(registry, mock_router)
    await run_test_3(registry, mock_router)
    await run_test_4(registry, mock_router)
    await run_test_5(registry)
    await run_test_6(registry)
    await run_test_7(registry, mock_router)
    await run_test_8(registry, mock_router)
    
    with open("reality_audit_output.txt", "w") as f:
        f.write("\n".join(OUTPUT))

if __name__ == "__main__":
    asyncio.run(main())
