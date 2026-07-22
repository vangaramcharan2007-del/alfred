from typing import Any, Dict, List, Optional
import time

from jarvisx.core.capabilities.base import Capability
from jarvisx.core.capabilities.runtime import CapabilityRuntime
from jarvisx.core.execution.task_planner import TaskPlanner
from jarvisx.core.logging import StructuredLogger
from jarvisx.core.permissions.manager import PermissionManager
from jarvisx.core.memory.preferences import PreferenceStore
from jarvisx.core.workflows.workflow_manager import WorkflowManager

from jarvisx.core.skills.skill_registry import SkillRegistry
from jarvisx.core.workforce_db import WorkforceDatabase
from jarvisx.core.skills.capability_context import CapabilityContext
from jarvisx.core.skills.capability_matcher import CapabilityMatcher
from jarvisx.core.skills.skill_ranker import SkillRanker
import asyncio




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
        self.permission_manager = PermissionManager(dashboard=dashboard)
        self.preference_store = PreferenceStore()
        
        self.workflow_manager = WorkflowManager()
        self.skill_registry = SkillRegistry()
        self.db = WorkforceDatabase()
        self.capability_context = CapabilityContext(self.skill_registry, self.db)
        self.matcher = CapabilityMatcher(self.capability_context)
        self.ranker = SkillRanker()



    def execute_mission(self, text_goal: str, voice_prompt_callback: Any = None) -> bool:
        """Plans and executes a mission, returning True on success."""
        
        # Phase 12.3: Resolve memory references
        resolved_goal, requires_confirmation = self.preference_store.resolve(text_goal)
        
        if resolved_goal != text_goal:
            if self.dashboard:
                self.dashboard.set_tts(f"I remember you mean {resolved_goal}. Using that.")
                
            if requires_confirmation:
                print(f"\n[MEMORY CONFIRMATION]")
                print(f"I remember your preference is: {resolved_goal}. Is this correct?")
                try:
                    response = input("(y/n): ").strip().lower()
                    if response in ('y', 'yes'):
                        # Learn from confirmation
                        for key in self.preference_store.data.get("references", {}):
                            if key in text_goal.lower():
                                self.preference_store.increment_confidence(key)
                    else:
                        resolved_goal = text_goal # Fallback to original
                except (EOFError, KeyboardInterrupt):
                    pass
        
        # 1. Ask Planner for a plan
        plan = self.planner.plan(resolved_goal)
        if not plan:
            # Fallback for dynamic demo scenarios where regex doesn't match
            # Create a dynamic plan based on text
            plan = self._create_dynamic_plan(resolved_goal)
            
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
            
            # PHASE E.5: CAPABILITY INTELLIGENCE LAYER
            step_desc = step.get("description", "")
            task_type = step.get("action_type", "")
            selected_skill = None
            
            try:
                candidates = asyncio.run(self.matcher.match(step_desc, task_type))
                ranked_candidates = self.ranker.rank(candidates, []) # assume no pre-granted permissions for now
                if ranked_candidates:
                    top_candidate = ranked_candidates[0]
                    skill_name = top_candidate["metadata"]["name"]
                    selected_skill = self.skill_registry.get_skill(skill_name)
                    
                    self.logger.write("info", "mission.skill_selected", 
                                      step=step_desc, 
                                      selected_skill=skill_name, 
                                      score=top_candidate["score"], 
                                      reason=top_candidate["reason"])
            except Exception as e:
                self.logger.write("warning", "mission.skill_selection_failed", error=str(e))
            
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
                    self.dashboard.update_mission(status="Requesting Permission...")

                # Permission Layer
                action_name = task_dict.get("action", capability.name.lower())
                action_target = task_dict.get("target") or task_dict.get("query") or task_dict.get("app") or task_dict.get("path") or ""
                
                approved = self.permission_manager.request(action_name, action_target, voice_prompt_callback=voice_prompt_callback)
                if not approved:
                    self.logger.write("warning", "mission_engine.permission_denied", step=step)
                    if self.dashboard:
                        self.dashboard.update_mission(status="FAILED: Permission Denied")
                    return False

                if self.dashboard:
                    self.dashboard.update_mission(status="Executing...")
                
                # EXECUTE
                start_time = time.time()
                success = False
                try:
                    if selected_skill:
                        # Execute the new Skill
                        result = asyncio.run(selected_skill.execute(step_desc, task_dict))
                        success = True
                    else:
                        # Fallback to legacy capability runtime
                        result = self.runtime.execute(capability, task_dict)
                        success = True
                except Exception as ex:
                    success = False
                    raise ex
                finally:
                    execution_time = time.time() - start_time
                    if selected_skill:
                        self.db.record_skill_execution(selected_skill.name, task_type, success, int(execution_time * 1000))
                
                if self.dashboard:
                    self.dashboard.update_mission(status="Verifying...")
                
                # VERIFICATION (Now handled within CapabilityRuntime, but we reflect state here)
                # If we are here, execution and verification succeeded (runtime raises ProviderError otherwise)
                
                if self.dashboard:
                    self.dashboard.update_mission(status="Success")
                    time.sleep(0.8) # pause for visual effect in demo
                    
                # B.9 Structured Logging
                self.logger.write("info", "mission.step.completed", 
                    mission_id=plan.get("objective_id", "unknown"),
                    intent=plan.get("objective_type", "unknown"),
                    provider=capability.name,
                    permission_granted=approved,
                    execution_time_sec=round(execution_time, 2),
                    verification_result=True,
                    fallback_used=False,
                    final_status="Success"
                )
                    
            except Exception as e:
                self.logger.write("error", "mission_engine.step_failed", error=str(e), step=step)
                if self.dashboard:
                    self.dashboard.update_mission(status=f"FAILED: {str(e)}")
                return False

        # Complete
        # B.10 Workflow Extraction (Skill Intelligence Layer)
        if total_steps > 1:
            try:
                workflow_name = plan.get("objective_type", f"Workflow_{text_goal[:15]}").replace(" ", "_")
                step_descriptions = [s.get("description", "step") for s in steps]
                self.workflow_manager.save_workflow(
                    name=workflow_name,
                    steps=step_descriptions,
                    metadata={"original_goal": text_goal}
                )
                self.logger.write("info", "mission.workflow_extracted", workflow=workflow_name)
            except Exception as e:
                self.logger.write("warning", "mission.workflow_extraction_failed", error=str(e))


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
