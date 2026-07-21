from typing import Any, Dict, List, Optional
import time

from jarvisx.core.capabilities.base import Capability
from jarvisx.core.capabilities.runtime import CapabilityRuntime
from jarvisx.core.execution.task_planner import TaskPlanner
from jarvisx.core.logging import StructuredLogger


class MissionEngine:
    """
    Executes a multi-step objective by querying the Planner and driving the CapabilityRuntime.
    Provides live status updates to the Dashboard.
    """

    def __init__(self, capability_runtime: CapabilityRuntime, dashboard: Any = None):
        self.planner = TaskPlanner()
        self.runtime = capability_runtime
        self.dashboard = dashboard
        self.logger = StructuredLogger()

    def execute_mission(self, text_goal: str) -> bool:
        """Plans and executes a mission, returning True on success."""
        
        # 1. Ask Planner for a plan
        plan = self.planner.plan(text_goal)
        if not plan:
            # Fallback for dynamic demo scenarios where regex doesn't match
            # Create a dynamic plan based on text
            plan = self._create_dynamic_plan(text_goal)
            
        steps = plan.get("steps", [])
        total_steps = len(steps)
        
        if total_steps == 0:
            return False

        if self.dashboard:
            self.dashboard.update_mission(
                running=True,
                progress=0,
                current_step="Initializing...",
                next_step=steps[0]["description"] if steps else "None",
                capability="PLANNER",
                provider="Alfred",
                status="Plan Generated"
            )

        # 2. Execute Steps
        for i, step in enumerate(steps):
            progress = int((i / total_steps) * 100)
            
            next_step_desc = steps[i+1]["description"] if i + 1 < total_steps else "Mission Complete"
            
            if self.dashboard:
                self.dashboard.update_mission(
                    progress=progress,
                    current_step=step["description"],
                    next_step=next_step_desc,
                    status="Negotiating capability..."
                )
                self.dashboard.clear_negotiation()

            # Map the legacy Action Type to a Capability
            capability, task_dict = self._map_action_to_capability(step)
            
            if self.dashboard:
                self.dashboard.update_mission(capability=capability.name)
                
                # Show negotiation preview
                evaluations = []
                for p in self.runtime.registry.get_all(capability):
                    try:
                        ev = p.evaluate(task_dict)
                        evaluations.append(ev)
                    except:
                        pass
                if evaluations:
                    # simplistic preview just for UI
                    evaluations.sort(key=lambda x: x.score, reverse=True)
                    self.dashboard.set_negotiation(
                        capability.name, 
                        evaluations, 
                        evaluations[0].provider_name if evaluations else "None"
                    )

            try:
                if self.dashboard:
                    self.dashboard.update_mission(status="Executing...")
                
                # EXECUTE
                self.runtime.execute(capability, task_dict)
                
                if self.dashboard:
                    self.dashboard.update_mission(status="Success")
                    time.sleep(0.8) # pause for visual effect in demo
                    
            except Exception as e:
                self.logger.write("error", "mission_engine.step_failed", error=str(e), step=step)
                if self.dashboard:
                    self.dashboard.update_mission(status=f"FAILED: {str(e)}")
                return False

        # Complete
        if self.dashboard:
            self.dashboard.update_mission(
                progress=100,
                current_step="All steps complete.",
                next_step="None",
                status="Mission Complete"
            )
            time.sleep(1)
            self.dashboard.update_mission(running=False)
            
        return True

    def _map_action_to_capability(self, step: dict) -> tuple[Capability, dict]:
        """Maps legacy task_planner action_types to the new Capability enum."""
        action = step.get("action_type", "")
        target = step.get("target", "")
        
        if action == "SEARCH_GOOGLE":
            return Capability.BROWSER, {"action": "search", "query": target}
        elif action == "OPEN_APPLICATION":
            return Capability.DESKTOP, {"action": "launch", "app": target}
        elif action == "CREATE_FOLDER_DIRECT" or action == "CREATE_FILE_DIRECT":
            return Capability.FILE_SYSTEM, {"action": "create", "path": target}
        elif action == "TYPE_TEXT" or action == "PRESS_SHORTCUT":
            return Capability.DESKTOP, {"action": action.lower(), "target": target}
        
        # Fallback
        return Capability.DESKTOP, {"action": "unknown", "target": target}

    def _create_dynamic_plan(self, text: str) -> dict:
        """Dynamic plan generator for unmapped voice intents (for the demo)."""
        text_lower = text.lower()
        if "prepare me for tomorrow's" in text_lower:
            return {
                "objective_type": "PREPARE_STUDY_PLAN",
                "steps": [
                    {"description": "Check timetable", "action_type": "SEARCH_GOOGLE", "target": "university timetable"},
                    {"description": "Search resources", "action_type": "SEARCH_GOOGLE", "target": "OS lab notes"},
                    {"description": "Create study checklist", "action_type": "CREATE_FILE_DIRECT", "target": "checklist.txt"}
                ]
            }
        elif "open github" in text_lower:
            return {
                "objective_type": "OPEN_GITHUB",
                "steps": [{"description": "Opening GitHub", "action_type": "SEARCH_GOOGLE", "target": "github.com"}]
            }
        elif "create folder demo" in text_lower or "create a folder named demo" in text_lower:
            return {
                "objective_type": "CREATE_FOLDER",
                "steps": [{"description": "Creating Folder Demo", "action_type": "CREATE_FOLDER_DIRECT", "target": "Demo"}]
            }
        elif "open vs code" in text_lower:
            return {
                "objective_type": "LAUNCH_APP",
                "steps": [{"description": "Launching VS Code", "action_type": "OPEN_APPLICATION", "target": "vscode"}]
            }
        return {"steps": []}
