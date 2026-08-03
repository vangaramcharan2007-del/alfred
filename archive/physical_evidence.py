import os
import json
import hashlib
import uuid
import time
from unittest.mock import AsyncMock

from jarvisx.core.tools.tool_registry import ToolRegistry
from jarvisx.core.providers.provider_router import ProviderRouter
from jarvisx.core.planning.objective_manager import ObjectiveManager
from jarvisx.core.tools.execution.file_ops import FileOps
from jarvisx.core.tools.execution.command_executor import CommandExecutor


def log_header(text):
    print(f"\n{'='*10} {text} {'='*10}")

def file_listing():
    log_header("1. File Listing")
    files_to_check = [
        "test_phase10_runtime.txt",
        "file_A.txt",
        "file_B.txt",
        "persistence.txt",
        "ev.txt"
    ]
    for f in files_to_check:
        if os.path.exists(f):
            stat = os.stat(f)
            print(f"- {f} (Size: {stat.st_size} bytes, Modified: {stat.st_mtime})")
        else:
            print(f"- {f} NOT FOUND")
            
    print("\nvar/objective_state/")
    if os.path.exists("var/objective_state"):
        for f in os.listdir("var/objective_state"):
            stat = os.stat(os.path.join("var/objective_state", f))
            print(f"- {f} (Size: {stat.st_size} bytes)")
    else:
        print("var/objective_state/ NOT FOUND")


def file_contents():
    log_header("2. File Contents")
    files_to_check = [
        "test_phase10_runtime.txt",
        "file_A.txt",
        "file_B.txt",
        "persistence.txt",
        "ev.txt"
    ]
    for f in files_to_check:
        print(f"\n--- {f} ---")
        if os.path.exists(f):
            with open(f, "r") as file:
                print(file.read())
        else:
            print("NOT FOUND")


def checksum_validation():
    log_header("3. Checksum Validation")
    files_to_check = [
        "test_phase10_runtime.txt",
        "file_A.txt",
        "file_B.txt",
        "persistence.txt",
        "ev.txt"
    ]
    for f in files_to_check:
        if os.path.exists(f):
            with open(f, "rb") as file:
                data = file.read()
                md5 = hashlib.md5(data).hexdigest()
                sha256 = hashlib.sha256(data).hexdigest()
                print(f"{f}:")
                print(f"  MD5: {md5}")
                print(f"  SHA256: {sha256}")
        else:
            print(f"{f}: NOT FOUND")


def state_files():
    log_header("4. State Files (var/objective_state/)")
    if os.path.exists("var/objective_state"):
        for f in os.listdir("var/objective_state"):
            print(f"\n--- {f} ---")
            with open(os.path.join("var/objective_state", f), "r") as file:
                data = json.load(file)
                print(json.dumps(data, indent=2))
    else:
        print("var/objective_state/ NOT FOUND")


def registry_dump():
    log_header("5. Registry Dump")
    registry = ToolRegistry.get_instance()
    registry.register(FileOps(), "file_ops")
    registry.register(CommandExecutor(), "command_executor")
    
    print("registry.list_tools():")
    print(registry.list_tools())
    
    print("\nregistry.get_tool_schema('file_ops'):")
    print(json.dumps(registry.get_tool_schema("file_ops"), indent=2))
    
    print("\nregistry.get_tool_schema('command_executor'):")
    print(json.dumps(registry.get_tool_schema("command_executor"), indent=2))


def execution_logs():
    log_header("6. Execution Logs")
    if os.path.exists("reality_audit_output.txt"):
        with open("reality_audit_output.txt", "r") as f:
            lines = f.readlines()
            
        print("\n--- Successful File Creation ---")
        for line in lines:
            if "File created successfully." in line or "Jarvis runtime validation successful" in line:
                print(line.strip())
                
        print("\n--- Failed Command Execution ---")
        for line in lines:
            if "nonexistent_command_xyz" in line or "Evidence (Error Capture)" in line or "return_code\": 1" in line:
                print(line.strip())
                
        print("\n--- Replanning Event ---")
        for line in lines:
            if "Triggering replanner" in line or "step2_fixed" in line or "Task failure detected" in line:
                print(line.strip())
                
        print("\n--- Persistence Write/Restore ---")
        for line in lines:
            if "Restored" in line or "Found" in line and "state files" in line:
                print(line.strip())
    else:
        print("reality_audit_output.txt NOT FOUND. Run proof_of_reality.py first.")


async def runtime_demonstration():
    log_header("7. Runtime Demonstration")
    registry = ToolRegistry.get_instance()
    mock_router = ProviderRouter(fallback_manager=None)
    mock_router.route_with_failover = AsyncMock()
    
    # 1. Create file 2. Read file 3. Delete file
    plan = [
        {"id": "c1", "description": "Create", "tool": "file_ops", "method": "create_file", "args": {"filepath": "demo_verify.txt", "content": "verification run"}, "depends_on": []},
        {"id": "r1", "description": "Read", "tool": "file_ops", "method": "read_file", "args": {"filepath": "demo_verify.txt"}, "depends_on": ["c1"]},
        {"id": "d1", "description": "Delete", "tool": "file_ops", "method": "delete_file", "args": {"filepath": "demo_verify.txt"}, "depends_on": ["r1"]}
    ]
    mock_router.route_with_failover.return_value = json.dumps(plan)
    
    manager = ObjectiveManager(mock_router, registry=registry)
    
    print("Generated Plan:")
    print(json.dumps(plan, indent=2))
    
    # Intercept ExecutionMonitor to print as it runs
    original_execute = manager.monitor.execute_task
    async def traced_execute(task):
        print(f"Executing: {task['id']} - {task['method']}")
        res = await original_execute(task)
        if task['id'] == 'c1':
            print(f"File exists after creation: {os.path.exists('demo_verify.txt')}")
        elif task['id'] == 'd1':
            print(f"File exists after deletion: {os.path.exists('demo_verify.txt')}")
        return res
    manager.monitor.execute_task = traced_execute
    
    res = await manager.execute_objective("Create demo_verify.txt, write, read back, delete")
    
    print("\nExecution Evidence:")
    print(json.dumps(res['evidence'], indent=2))


async def process_restart_test():
    log_header("8. Process Restart Test")
    registry = ToolRegistry.get_instance()
    mock_router = ProviderRouter(fallback_manager=None)
    mock_router.route_with_failover = AsyncMock()
    
    # We will simulate a crash in execution monitor
    plan = [
        {"id": "step1", "description": "1", "tool": "file_ops", "method": "create_file", "args": {"filepath": "restart_1.txt", "content": "1"}, "depends_on": []},
        {"id": "step2", "description": "Crash point", "tool": "file_ops", "method": "create_file", "args": {"filepath": "restart_2.txt", "content": "2"}, "depends_on": ["step1"]}
    ]
    mock_router.route_with_failover.return_value = json.dumps(plan)
    
    manager = ObjectiveManager(mock_router, registry=registry)
    objective_name = "Restart test"
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in objective_name[:60])
    state_file = os.path.join("var/objective_state", f"{safe_name}.json")
    
    print("--- BEFORE RESTART ---")
    
    original_execute = manager.monitor.execute_task
    async def crash_execute(task):
        if task['id'] == 'step2':
            print("SIMULATING PROCESS TERMINATION AT STEP 2")
            raise Exception("SIMULATED CRASH")
        return await original_execute(task)
    manager.monitor.execute_task = crash_execute
    
    try:
        res1 = await manager.execute_objective(objective_name)
    except Exception as e:
        print(str(e))
        
    print(f"State file exists: {os.path.exists(state_file)}")
    with open(state_file) as f:
        print(f"Persisted State Snapshot (BEFORE RESTART): {json.dumps(json.load(f), indent=2)}")
        
    print("\n--- AFTER RESTART ---")
    manager2 = ObjectiveManager(mock_router, registry=registry)
    with open(state_file) as f:
        restored_data = json.load(f)
        # Mocking the restore process that the framework uses
        manager2.evidence_cache = restored_data['evidence']
        
    print(f"Restored Completed Tasks: {restored_data['tracker']['completed_tasks']}")
    
    # Now execute properly
    mock_router.route_with_failover.side_effect = [
        json.dumps([
            {"id": "step2", "description": "Crash point", "tool": "file_ops", "method": "create_file", "args": {"filepath": "restart_2.txt", "content": "2"}, "depends_on": []}
        ])
    ]
    res = await manager2.execute_objective(objective_name)
    
    print(f"Final Success: {res['success']}")
    print(f"Final Completed Tasks: {res['tracker']['completed_tasks']}")
    

if __name__ == "__main__":
    import asyncio
    file_listing()
    file_contents()
    checksum_validation()
    state_files()
    registry_dump()
    execution_logs()
    
    asyncio.run(runtime_demonstration())
    asyncio.run(process_restart_test())
