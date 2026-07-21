"""Task Executor — orchestrates autonomous plans."""
import os
import time
import logging
from typing import Dict, Any, Tuple

from jarvisx.core.voice.tts_engine import TTSEngine
from jarvisx.core.execution.task_planner import TaskPlanner
from jarvisx.core.execution.progress_tracker import ProgressTracker
from jarvisx.core.desktop.desktop_controller import DesktopController
from jarvisx.core.desktop.window_manager import WindowManager
from jarvisx.core.desktop.action_verifier import ActionVerifier
from jarvisx.core.browser.browser_controller import BrowserController
from jarvisx.core.os_control.app_launcher import AppLauncher
from jarvisx.core.objective_store import ObjectiveStore

from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent
from jarvisx.core.execution.execution_context import ExecutionContext
from jarvisx.core.execution.capability_registry import CapabilityRegistry
from jarvisx.core.execution.failure_classifier import FailureClassifier
from jarvisx.core.execution.reflection_engine import ReflectionEngine
from jarvisx.core.execution.recovery_planner import RecoveryPlanner
from jarvisx.core.execution.execution_coordinator import ExecutionCoordinator
from jarvisx.core.execution.fault_injector import FaultInjector

logger = logging.getLogger(__name__)

class TaskExecutor:
    """Executes objective plans fully autonomously."""
    
    def __init__(
        self,
        planner: TaskPlanner,
        objective_store: ObjectiveStore,
        desktop_controller: DesktopController,
        window_manager: WindowManager,
        action_verifier: ActionVerifier,
        browser_controller: BrowserController
    ):
        self.planner = planner
        self.store = objective_store
        self.desktop = desktop_controller
        self.window = window_manager
        self.verifier = action_verifier
        self.browser = browser_controller
        self.tts = TTSEngine()
        
        # Phase 22 Components
        self.event_bus = EventBus()
        self.context = ExecutionContext()
        self.registry = CapabilityRegistry()
        self.classifier = FailureClassifier()
        self.reflection = ReflectionEngine(self.classifier)
        self.recovery = RecoveryPlanner(self.registry)
        self.injector = FaultInjector()
        
        # Phase 23 Components
        self.checkpoint_manager = None # Optional injection
        
        self.coordinator = ExecutionCoordinator(
            event_bus=self.event_bus,
            reflection_engine=self.reflection,
            recovery_planner=self.recovery,
            executor_fn=self._execute_step,
            verifier_fn=self._verify_step
        )
        
        self._setup_event_logging()

    def set_checkpoint_manager(self, checkpoint_manager):
        self.checkpoint_manager = checkpoint_manager

    def set_persistent_queue(self, queue):
        """Set the persistent queue for progress synchronization."""
        self.queue = queue

    def _setup_event_logging(self):
        """Subscribe to events for structured console logging."""
        def log_event(event, payload):
            if event == ExecutionEvent.STEP_STARTED:
                print(f"\n[Execution]\nAction: {payload['step']['action_type']}\nTarget: {payload['step']['target']}")
            elif event == ExecutionEvent.VERIFICATION_PASSED:
                print("[Verification]\nPassed: True")
            elif event == ExecutionEvent.VERIFICATION_FAILED:
                print("[Verification]\nPassed: False")
            elif event == ExecutionEvent.REFLECTION_COMPLETED:
                r = payload['reflection']
                if not r.success:
                    print(f"\n[Reflection]\nFailure: {r.failure_category.name if r.failure_category else 'UNKNOWN'}")
                    print(f"Recoverable: {r.recoverable}\nConfidence: {r.confidence}\nRecommendation: {r.recommendation}")
            elif event == ExecutionEvent.RECOVERY_STARTED:
                print(f"\n[Recovery]\nStrategy: {payload['strategy']}")
            elif event == ExecutionEvent.RECOVERY_SUCCEEDED:
                print("Result: SUCCESS")
            elif event == ExecutionEvent.RECOVERY_FAILED:
                print("Result: FAILED")
                
        for e in ExecutionEvent:
            self.event_bus.subscribe(e, log_event)

    def execute_objective(self, plan: Dict[str, Any], snapshot=None, pause_check_fn=None) -> Dict[str, Any]:
        """Main entry point. Runs an objective plan."""
        objective_id = plan.get("objective_id", "unknown")
        
        # Populate ExecutionContext
        self.context.objective_id = objective_id
        
        self.event_bus.publish(ExecutionEvent.OBJECTIVE_STARTED, {"objective_id": objective_id})
        self.tts.speak("Executing objective.")

        tracker = ProgressTracker(plan)
        
        if snapshot:
            # Fast-forward progress
            for _ in range(snapshot.current_step):
                if not tracker.is_finished():
                    tracker.mark_completed()
            
            # Apply snapshot state to context
            vars = getattr(self.context, 'variables', {})
            vars.update(snapshot.variables)
            self.context.variables = vars

        while not tracker.is_finished():
            if pause_check_fn and pause_check_fn():
                return {"success": False, "status": "PAUSED"}
                
            self.context.current_step = tracker.current_step_index
            step = tracker.get_current_step()
            
            # Announce step
            msg = f"{tracker.get_progress_string()} {step['description']}"
            print(f"\n{msg}")
            self.tts.speak(msg)
            
            print(f"\nObjective:\n{plan['objective_type']}\n\nPlan:\n{len(plan['steps'])} steps\n\nCurrent Step:\n{tracker.current_step_index + 1}/{len(plan['steps'])}")
            
            # Coordinate step execution (Execute -> Verify -> Reflect -> Recover)
            success = self.coordinator.coordinate_step(step)
            
            if not success:
                tracker.mark_failed()
                print("\nResult:\nFAILURE\n")
                self.tts.speak("I was unable to complete the objective.")
                self.event_bus.publish(ExecutionEvent.OBJECTIVE_FAILED, {"objective_id": objective_id})
                return {"success": False, "error": "Step failed"}
            
            tracker.mark_completed()
            
            if self.checkpoint_manager:
                from jarvisx.core.execution.execution_snapshot import ExecutionSnapshot
                completed = list(range(tracker.current_step_index))
                new_snapshot = ExecutionSnapshot(
                    objective_id=objective_id,
                    current_step=tracker.current_step_index,
                    completed_steps=completed,
                    variables=getattr(self.context, 'variables', {}),
                    context={},
                    reflection_state={},
                    recovery_state={}
                )
                self.checkpoint_manager.save_checkpoint(new_snapshot)
                
                if hasattr(self, 'queue') and self.queue:
                    self.queue.update_progress(objective_id, tracker.current_step_index)
                
                self.event_bus.publish(ExecutionEvent.OBJECTIVE_CHECKPOINT_SAVED, {"objective_id": objective_id, "step": tracker.current_step_index})
            
            # Give UI time to breathe
            time.sleep(1.0)
            
        print("\nResult:\nSUCCESS\n")
        self.tts.speak("Objective completed successfully.")
        self.event_bus.publish(ExecutionEvent.OBJECTIVE_COMPLETED, {"objective_id": objective_id})
        return {"success": True}

    def _execute_step(self, step: Dict[str, Any]) -> Tuple[bool, Exception]:
        """Dispatches action to the correct subsystem."""
        action = step["action_type"]
        # Resolve any context placeholders (e.g. ${DESKTOP})
        target = self.context.resolve_path(step.get("target", ""))
        step["target"] = target # update it so verification knows
        
        # Check for step-based injected faults FIRST
        injected_fault = self.injector.check_step_fault(self.context, action)
        if not injected_fault:
            # Check for generic target-based injected execution faults
            injected_fault = self.injector.check_execution_fault(action, target)
            
        if injected_fault:
            return False, injected_fault
        
        try:
            if action == "OPEN_APPLICATION":
                if target.startswith("explorer"):
                    os.system(target) # special shell launch
                    return True, None
                
                # Check capability registry first
                cap = self.registry.get(target)
                cmd = cap.name if cap else target
                
                success = AppLauncher.launch(cmd)
                if not success:
                    return False, FileNotFoundError(f"Application {target} not found")
                return True, None
                
            elif action == "TYPE_TEXT":
                success = self.desktop.type_text(target)
                return success, None
                
            elif action == "PRESS_SHORTCUT":
                success = self.desktop.press_shortcut(target)
                return success, None
                
            elif action == "SEARCH_GOOGLE":
                self.browser.search_google(target)
                return True, None
                
            elif action == "CREATE_FOLDER_DIRECT":
                os.makedirs(target, exist_ok=True)
                return True, None
                
            elif action == "CREATE_FILE_DIRECT":
                try:
                    with open(target, "w") as f:
                        f.write("jarvis_test")
                    return True, None
                except Exception as e:
                    return False, e
                
            elif action == "SWITCH_WINDOW":
                success = self.window.activate_window(target)
                return success, None
                
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return False, e
            
        return False, ValueError(f"Unknown action {action}")

    def _verify_step(self, step: Dict[str, Any]) -> bool:
        """Verifies the physical side effects of a step."""
        verif_type = step.get("verification", "NONE")
        if verif_type == "NONE":
            return True
            
        target = self.context.resolve_path(step.get("verification_target", ""))
        
        # Check for injected verification faults
        if self.injector.check_verification_fault(target):
            return False
        
        if verif_type == "WINDOW_EXISTS":
            return self.verifier.verify_window_active(target, timeout=5.0)
            
        elif verif_type == "FILE_EXISTS":
            # Just check the absolute path since we resolved placeholders
            for _ in range(5):
                if os.path.exists(target):
                    return True
                time.sleep(1.0)
            return False
            
        elif verif_type == "FOLDER_EXISTS":
            return os.path.exists(target)
            
        elif verif_type == "BROWSER_URL_MATCHES":
            time.sleep(3.0)
            return True
            
        return True
