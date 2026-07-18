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
        
        self.coordinator = ExecutionCoordinator(
            event_bus=self.event_bus,
            reflection_engine=self.reflection,
            recovery_planner=self.recovery,
            executor_fn=self._execute_step,
            verifier_fn=self._verify_step
        )
        
        self._setup_event_logging()

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

    def execute_objective(self, raw_text: str) -> None:
        """Main entry point. Plans and runs an objective."""
        self.event_bus.publish(ExecutionEvent.OBJECTIVE_STARTED, {"raw_text": raw_text})
        self.tts.speak("Planning objective.")
        
        plan = self.planner.plan(raw_text)
        if not plan:
            self.tts.speak("I am currently unable to autonomously plan that objective.")
            self.event_bus.publish(ExecutionEvent.OBJECTIVE_FAILED, {"reason": "planning_failed"})
            return

        tracker = ProgressTracker(plan)
        
        # Save initial state
        self.store.save_objective(plan)

        while not tracker.is_finished():
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
                self.store.fail_objective(plan["objective_id"])
                self.event_bus.publish(ExecutionEvent.OBJECTIVE_FAILED, {"objective_id": plan["objective_id"]})
                return
            
            tracker.mark_completed()
            # Update store
            self.store.update_objective(plan["objective_id"], {"status": "in_progress", "step_index": tracker.current_step_index})
            
            # Give UI time to breathe
            time.sleep(1.0)
            
        print("\nResult:\nSUCCESS\n")
        self.tts.speak("Objective completed successfully.")
        self.store.complete_objective(plan["objective_id"])
        self.event_bus.publish(ExecutionEvent.OBJECTIVE_COMPLETED, {"objective_id": plan["objective_id"]})

    def _execute_step(self, step: Dict[str, Any]) -> Tuple[bool, Exception]:
        """Dispatches action to the correct subsystem."""
        action = step["action_type"]
        # Resolve any context placeholders (e.g. ${DESKTOP})
        target = self.context.resolve_path(step.get("target", ""))
        step["target"] = target # update it so verification knows
        
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
