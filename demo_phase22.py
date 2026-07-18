import sys
import os
import time

# Add src to python path for imports
sys.path.insert(0, os.path.abspath("src"))

from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent
from jarvisx.core.execution.fault_injector import FaultInjector
from jarvisx.core.execution.task_executor import TaskExecutor
from jarvisx.core.execution.task_planner import TaskPlanner
from jarvisx.core.execution.capability_registry import Capability
from jarvisx.core.objective_store import ObjectiveStore
from jarvisx.core.desktop.desktop_controller import DesktopController
from jarvisx.core.desktop.window_manager import WindowManager
from jarvisx.core.desktop.action_verifier import ActionVerifier
from jarvisx.core.browser.browser_controller import BrowserController


def main():
    print("==================================================")
    print("  PHASE 22.1: REAL-WORLD VALIDATION DEMO")
    print("==================================================\n")

    # Initialize real components
    planner = TaskPlanner()
    store = ObjectiveStore()
    desktop = DesktopController()
    window = WindowManager()
    verifier = ActionVerifier(window_manager=window)
    browser = BrowserController()

    executor = TaskExecutor(
        planner=planner,
        objective_store=store,
        desktop_controller=desktop,
        window_manager=window,
        action_verifier=verifier,
        browser_controller=browser
    )

    # Disable TTS for the demo to prevent hanging in headless environments
    executor.tts.speak = lambda text: None

    injector = FaultInjector()
    
    # Register capabilities so recovery knows alternatives
    executor.registry.register(Capability("chrome", description="browser", alternatives=["edge", "firefox"]))
    executor.registry.register(Capability("notepad++", description="editor", alternatives=["notepad"]))
    
    # Store scenario results
    results = {}

    print("--- SCENARIO 1: Missing Application (Fallback to Alternative) ---")
    # We want to open Chrome. We inject a fault so "chrome" fails.
    # The Recovery Planner should see missing app -> alternative tool -> use Edge.
    # The physical result should be Edge opening.
    
    injector.inject_execution_fault("OPEN_APPLICATION", "chrome", FileNotFoundError("chrome.exe not found"))
    executor.execute_objective("launch chrome")
    
    # Verify: did it succeed? The executor handles logging.
    # In a real validation, we can check if the Edge window exists.
    time.sleep(3)
    opened = verifier.verify_window_active("edge", timeout=10.0)
    results["Scenario 1 (Missing Browser -> Edge Fallback)"] = "PASS" if opened else "FAIL"
    
    
    print("\n--- SCENARIO 2: Permission Denied (Switch Directory) ---")
    # We try to create a file in System32. Windows will naturally throw PermissionError 
    # when we use python's `open(..., 'w')` on that directory. 
    # Reflection should catch it -> PermissionRecoveryStrategy -> rewrite path to TEMP.
    
    target_path = "C:/Windows/System32/jarvis_test.txt"
    executor.execute_objective(f"create file at {target_path}")
    
    # Verify it was created in TEMP instead of System32
    import tempfile
    fallback_path = os.path.join(tempfile.gettempdir(), "jarvis_test.txt")
    if os.path.exists(fallback_path):
        results["Scenario 2 (Permission Denied -> Temp Directory Fallback)"] = "PASS"
        os.remove(fallback_path) # Clean up
    else:
        results["Scenario 2 (Permission Denied -> Temp Directory Fallback)"] = "FAIL"


    print("\n--- SCENARIO 3: Verification Failure (Retry Strategy) ---")
    # We create a file on the Desktop, but inject a verification fault on the first attempt.
    # Reflection should retry. The second verification attempt will not have the fault and will pass.
    
    desktop_file = os.path.join(os.path.expanduser("~"), "Desktop", "retry_test.txt")
    # Clean up before start
    if os.path.exists(desktop_file):
        os.remove(desktop_file)
        
    injector.inject_verification_fault(desktop_file)
    executor.execute_objective("create file at ${DESKTOP}/retry_test.txt")
    
    if os.path.exists(desktop_file):
        results["Scenario 3 (Verification Failure -> Retry)"] = "PASS"
        os.remove(desktop_file) # Clean up
    else:
        results["Scenario 3 (Verification Failure -> Retry)"] = "FAIL"


    print("\n--- SCENARIO 4: Capability Fallback Validation ---")
    # Notepad++ is registered with alternative "notepad". We inject a failure for notepad++.
    injector.inject_execution_fault("OPEN_APPLICATION", "notepad++", FileNotFoundError("Notepad++ missing"))
    executor.execute_objective("launch notepad++")
    
    time.sleep(3)
    # Check if Notepad (the alternative) actually opened
    opened_notepad = verifier.verify_window_active("Notepad", timeout=10.0)
    results["Scenario 4 (Capability Fallback -> Notepad)"] = "PASS" if opened_notepad else "FAIL"


    print("\n==================================================")
    print("  VISUAL VALIDATION SUMMARY")
    print("==================================================")
    
    all_passed = True
    for scenario, result in results.items():
        print(f"{scenario}\n{result}\n")
        if result == "FAIL":
            all_passed = False
            
    print(f"Overall\n{'PASS' if all_passed else 'FAIL'}")

if __name__ == "__main__":
    main()
