import sys
import os
import time

# Add src to python path for imports
sys.path.insert(0, os.path.abspath("src"))

from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent
from jarvisx.core.execution.execution_context import ExecutionContext
from jarvisx.core.execution.capability_registry import CapabilityRegistry
from jarvisx.core.execution.failure_classifier import FailureClassifier
from jarvisx.core.execution.reflection_engine import ReflectionEngine
from jarvisx.core.execution.recovery_planner import RecoveryPlanner
from jarvisx.core.execution.execution_coordinator import ExecutionCoordinator


def main():
    print("==================================================")
    print("  PHASE 22: REFLECTION & RECOVERY ENGINE DEMO")
    print("==================================================\n")

    event_bus = EventBus()
    context = ExecutionContext()
    registry = CapabilityRegistry()
    classifier = FailureClassifier()
    reflection = ReflectionEngine(classifier)
    recovery = RecoveryPlanner(registry)

    # 1. Live Event Stream Logger
    def log_event(event, payload):
        if event == ExecutionEvent.STEP_STARTED:
            print(f"\n[EventBus] -> STEP_STARTED: {payload['step']['action_type']} targeting {payload['step']['target']}")
        elif event == ExecutionEvent.VERIFICATION_FAILED:
            print(f"[EventBus] -> VERIFICATION_FAILED for {payload['step']['target']}")
        elif event == ExecutionEvent.REFLECTION_COMPLETED:
            r = payload['reflection']
            print(f"[EventBus] -> REFLECTION_COMPLETED:")
            print(f"            Success: {r.success}")
            if not r.success:
                print(f"            Failure: {r.failure_category.name if r.failure_category else 'UNKNOWN'}")
                print(f"            Recoverable: {r.recoverable}")
                print(f"            Recommendation: {r.recommendation}")
        elif event == ExecutionEvent.RECOVERY_STARTED:
            print(f"[EventBus] -> RECOVERY_STARTED (Strategy: {payload['strategy']})")
        elif event == ExecutionEvent.RECOVERY_SUCCEEDED:
            print(f"[EventBus] -> RECOVERY_SUCCEEDED!")
        elif event == ExecutionEvent.RECOVERY_FAILED:
            print(f"[EventBus] -> RECOVERY_FAILED!")

    for e in ExecutionEvent:
        event_bus.subscribe(e, log_event)

    # Variables to mock behaviors
    mock_state = {
        "fake_browser_opened": False,
        "verification_attempts": 0
    }

    # Dummy executor
    def executor_fn(step):
        action = step["action_type"]
        target = step["target"]
        target_resolved = context.resolve_path(target)
        
        if action == "OPEN_APPLICATION":
            # Simulate missing chrome
            if target == "chrome":
                return False, FileNotFoundError("chrome.exe not found")
            elif target == "edge":
                print(f"    [Executor] Opening {target} (Alternative fallback successful)")
                mock_state["fake_browser_opened"] = True
                return True, None
                
        elif action == "CREATE_FILE":
            # Simulate permission denied for system32
            if "system32" in target_resolved.lower():
                return False, PermissionError("Access is denied")
            else:
                print(f"    [Executor] Creating file at {target_resolved}")
                return True, None
                
        elif action == "VERIFY_ME":
            # Just succeed execution, fail verification first time
            return True, None

        return False, ValueError("Unknown action")

    # Dummy verifier
    def verifier_fn(step):
        if step["action_type"] == "VERIFY_ME":
            mock_state["verification_attempts"] += 1
            if mock_state["verification_attempts"] < 2:
                print("    [Verifier] Returning False (simulating verification fail)")
                return False
            print("    [Verifier] Returning True (simulating successful retry)")
            return True
        return True

    coordinator = ExecutionCoordinator(
        event_bus=event_bus,
        reflection_engine=reflection,
        recovery_planner=recovery,
        executor_fn=executor_fn,
        verifier_fn=verifier_fn
    )

    print("--- SCENARIO 1: Missing Application (Fallback to Alternative) ---")
    step1 = {"action_type": "OPEN_APPLICATION", "target": "chrome"}
    res1 = coordinator.coordinate_step(step1)
    print(f"\nScenario 1 Result: {'SUCCESS' if res1 else 'FAILED'}\n")

    print("--- SCENARIO 2: Permission Denied (Switch Directory) ---")
    # Using C:/Windows/System32 to trigger permission error
    step2 = {"action_type": "CREATE_FILE", "target": "C:/Windows/System32/config.sys"}
    res2 = coordinator.coordinate_step(step2)
    print(f"\nScenario 2 Result: {'SUCCESS' if res2 else 'FAILED'}\n")

    print("--- SCENARIO 3: Verification Failure (Retry Strategy) ---")
    step3 = {"action_type": "VERIFY_ME", "target": "something"}
    res3 = coordinator.coordinate_step(step3)
    print(f"\nScenario 3 Result: {'SUCCESS' if res3 else 'FAILED'}\n")

    print("==================================================")
    print("  DEMO COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    main()
