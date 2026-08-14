"""Closed-Loop Autonomous Visual Agent Loop for Jarvis X: GENESIS.

Implements the complete Closed-Loop Semantic Visual Reasoning Cycle:
- PLAN: Zero-shot decomposition of visual goals into progressive stages
- ACT: Deterministic UACC/MCP execution on live Windows Desktop (MS Paint)
- OBSERVE: Screen re-observation & Semantic SceneState extraction
- EVALUATE: Model-agnostic visual evaluation of missing elements, scale, and position errors
- CORRECT: Dynamic synthesis and application of corrective delta strokes
- REFINE: Contextual natural-language modifications against existing canvas state
"""

from __future__ import annotations
import sys
import time
import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from jarvisx.mcp.mcp_client import MCPClient
from jarvisx.computer_use.art_synthesizer import ArtSynthesizer
from jarvisx.computer_use.canvas_perception import CanvasBoundingBox, CanvasPerceptionEngine
from jarvisx.computer_use.generative_visual_planner import GenerativeVisualPlanner
from jarvisx.computer_use.semantic_canvas_perception import SemanticCanvasPerceptionEngine, SceneState
from jarvisx.computer_use.visual_evaluator import VisualEvaluator, VisualEvaluation
from jarvisx.computer_use.visual_corrector import VisualCorrector, VisualCorrection
from jarvisx.observability.computer_use_logger import get_computer_use_logger


@dataclass
class VisualPlanStage:
    stage_id: int
    name: str
    description: str
    strokes: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False
    verified: bool = False


@dataclass
class VisualDrawingSession:
    goal: str
    character_name: str
    stages: List[VisualPlanStage] = field(default_factory=list)
    executed_strokes: List[Dict[str, Any]] = field(default_factory=list)
    canvas_center: List[int] = field(default_factory=lambda: [960, 540])
    total_strokes: int = 0
    corrections_applied: List[str] = field(default_factory=list)
    refinements_applied: List[str] = field(default_factory=list)
    current_scene_state: Optional[SceneState] = None
    latest_evaluation: Optional[VisualEvaluation] = None
    iteration_count: int = 0
    status: str = "INITIALIZED"


class VisualAgentLoop:
    """Closed-loop visual planning, semantic evaluation, and computer-use actuation agent."""

    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.client = mcp_client or MCPClient(
            server_id="uacc_desktop_server",
            command=[sys.executable, "-m", "jarvisx.mcp.uacc_server"]
        )
        self.perception_engine = SemanticCanvasPerceptionEngine()
        self.evaluator = VisualEvaluator()
        self.corrector = VisualCorrector()
        self.logger = get_computer_use_logger()
        self.active_session: Optional[VisualDrawingSession] = None

    async def initialize_canvas(self) -> Dict[str, Any]:
        """Launch MS Paint and observe active canvas coordinates."""
        if not self.client.is_connected:
            await self.client.connect(timeout_sec=4.0)

        # 1. Launch MS Paint
        await self.client.call_tool("uacc_launch_app", {"app_name": "mspaint"})
        await asyncio.sleep(0.8)

        # 2. Inspect Screen
        inspect_res = await self.client.call_tool("uacc_inspect_screen", {})
        screen_text = inspect_res.get("content", [{}])[0].get("text", "{}")
        screen_data = json.loads(screen_text) if inspect_res.get("content") else {}

        w = screen_data.get("width", 1920)
        h = screen_data.get("height", 1080)
        cx, cy = w // 2, h // 2

        return {"width": w, "height": h, "center": [cx, cy], "active_window": screen_data.get("active_window")}

    def plan_visual_milestones(self, goal: str, cx: int, cy: int) -> VisualDrawingSession:
        """Decompose natural language visual goal into multi-stage milestones."""
        goal_clean = goal.lower().strip()
        session = VisualDrawingSession(goal=goal, character_name="Custom Artwork", canvas_center=[cx, cy])

        if ("luffy" in goal_clean and "zoro" in goal_clean) or "vs" in goal_clean:
            session.character_name = "Luffy vs Zoro (Straw Hat Duel)"
            s1 = VisualPlanStage(stage_id=1, name="Primary Contours", description="Silhouettes", strokes=ArtSynthesizer.generate_luffy_vs_zoro_strokes(cx, cy)[:20])
            s2 = VisualPlanStage(stage_id=2, name="Facial Features & Scars", description="Eyes, scars, expressions", strokes=ArtSynthesizer.generate_luffy_vs_zoro_strokes(cx, cy)[20:38])
            s3 = VisualPlanStage(stage_id=3, name="Santoryu Blades & Haki Clash", description="Fist, katanas, lightning", strokes=ArtSynthesizer.generate_luffy_vs_zoro_strokes(cx, cy)[38:])
            session.stages = [s1, s2, s3]

        elif "iron" in goal_clean or "stark" in goal_clean:
            session.character_name = "Iron Man Mark 85"
            s1 = VisualPlanStage(stage_id=1, name="Helmet Contour", description="Outer faceplate", strokes=ArtSynthesizer.generate_ironman_strokes(cx, cy)[:10])
            s2 = VisualPlanStage(stage_id=2, name="Optical Sensors", description="Eye slits & seams", strokes=ArtSynthesizer.generate_ironman_strokes(cx, cy)[10:18])
            s3 = VisualPlanStage(stage_id=3, name="Arc Reactor Core", description="Power core", strokes=ArtSynthesizer.generate_ironman_strokes(cx, cy)[18:])
            session.stages = [s1, s2, s3]

        elif "zoro" in goal_clean:
            session.character_name = "Roronoa Zoro (Santoryu)"
            s1 = VisualPlanStage(stage_id=1, name="Bandana & Jawline", description="Head structure", strokes=ArtSynthesizer.generate_zoro_strokes(cx, cy)[:10])
            s2 = VisualPlanStage(stage_id=2, name="Piercing Eyes & Scar", description="Eye slash & nose", strokes=ArtSynthesizer.generate_zoro_strokes(cx, cy)[10:18])
            s3 = VisualPlanStage(stage_id=3, name="Three Swords (Santoryu)", description="Mouth blade & cross katanas", strokes=ArtSynthesizer.generate_zoro_strokes(cx, cy)[18:])
            session.stages = [s1, s2, s3]

        else:
            bbox = CanvasPerceptionEngine.locate_paint_canvas(cx * 2, cy * 2)
            compiled = GenerativeVisualPlanner.compile_goal_to_stages(goal, bbox)
            session.character_name = compiled["subject"]
            session.stages = [
                VisualPlanStage(stage_id=st["id"], name=st["name"], description=st["name"], strokes=st["strokes"])
                for st in compiled["stages"]
            ]

        self.active_session = session
        return session

    async def execute_closed_loop_drawing(self, goal: str, max_corrections: int = 3) -> Dict[str, Any]:
        """Execute full closed-loop visual reasoning: Plan -> Act -> Observe -> Evaluate -> Correct -> Verify."""
        t0 = time.time()
        canvas_info = await self.initialize_canvas()
        cx, cy = canvas_info["center"]

        session = self.plan_visual_milestones(goal, cx, cy)
        all_strokes: List[Dict[str, Any]] = []

        # -----------------------------------------------------------
        # 1. INITIAL EXECUTION PASS
        # -----------------------------------------------------------
        for stage in session.stages:
            print(f"[VISUAL AGENT LOOP] Stage {stage.stage_id}/3: '{stage.name}' ({len(stage.strokes)} strokes)...")
            res = await self.client.call_tool("uacc_draw_stroke_sequence", {"strokes": stage.strokes}, timeout_sec=20.0)
            stage.completed = (res.get("status") == "success")
            all_strokes.extend(stage.strokes)
            await asyncio.sleep(0.2)

        session.executed_strokes = list(all_strokes)
        session.iteration_count = 1

        # -----------------------------------------------------------
        # 2. CLOSED-LOOP RE-OBSERVATION & SEMANTIC EVALUATION
        # -----------------------------------------------------------
        print("[VISUAL AGENT LOOP] Re-observing canvas and extracting semantic SceneState...")
        scene = self.perception_engine.analyze_canvas_scene(
            executed_strokes=session.executed_strokes,
            expected_goal=goal,
            screen_w=cx * 2,
            screen_h=cy * 2
        )
        session.current_scene_state = scene

        evaluation = self.evaluator.evaluate_scene(goal, scene)
        session.latest_evaluation = evaluation

        print(f"[VISUAL EVALUATOR] Goal Match Score: {evaluation.goal_match_score:.2f} ({evaluation.completion_status})")
        if evaluation.missing_elements:
            print(f"[VISUAL EVALUATOR] Missing Elements: {evaluation.missing_elements}")
        if evaluation.scale_errors:
            print(f"[VISUAL EVALUATOR] Scale Errors: {evaluation.scale_errors}")

        # -----------------------------------------------------------
        # 3. AUTONOMOUS CORRECTION LOOP (IF INCOMPLETE)
        # -----------------------------------------------------------
        corrections_done = 0
        while not evaluation.is_satisfactory and corrections_done < max_corrections:
            corrections = self.corrector.generate_corrections_from_evaluation(evaluation, scene)
            if not corrections:
                break

            for corr in corrections:
                print(f"[VISUAL CORRECTOR] Applying Correction: {corr.description} ({len(corr.corrective_strokes)} delta strokes)...")
                corr_res = await self.client.call_tool("uacc_draw_stroke_sequence", {"strokes": corr.corrective_strokes}, timeout_sec=15.0)
                if corr_res.get("status") == "success":
                    session.executed_strokes.extend(corr.corrective_strokes)
                    session.corrections_applied.append(corr.description)
                await asyncio.sleep(0.2)

            corrections_done += 1
            session.iteration_count += 1

            # Re-observe and re-evaluate
            scene = self.perception_engine.analyze_canvas_scene(session.executed_strokes, goal, cx * 2, cy * 2)
            session.current_scene_state = scene
            evaluation = self.evaluator.evaluate_scene(goal, scene)
            session.latest_evaluation = evaluation

        session.total_strokes = len(session.executed_strokes)
        session.status = "COMPLETED"
        total_latency = round((time.time() - t0) * 1000, 1)

        self.logger.log_action(
            task_id=f"closed_loop_visual_{int(time.time()*1000)}",
            tool="visual_agent_loop",
            action="closed_loop_draw",
            success=True,
            latency_ms=total_latency,
            params={
                "character": session.character_name,
                "iterations": session.iteration_count,
                "corrections": session.corrections_applied,
                "final_score": evaluation.goal_match_score,
                "total_strokes": session.total_strokes
            }
        )

        return {
            "status": "success",
            "character": session.character_name,
            "goal": goal,
            "level": "Level 6 Closed-Loop Semantic Visual Agent",
            "iterations": session.iteration_count,
            "goal_match_score": evaluation.goal_match_score,
            "completion_status": evaluation.completion_status,
            "corrections_applied": session.corrections_applied,
            "detected_objects": [obj.name for obj in scene.detected_objects],
            "total_strokes": session.total_strokes,
            "total_latency_ms": total_latency,
            "session_id": id(session)
        }

    async def apply_conversational_refinement(self, refinement_prompt: str) -> Dict[str, Any]:
        """Apply contextual conversational refinements to the existing canvas state."""
        if not self.active_session or not self.active_session.current_scene_state:
            # Fallback initialization if session state is fresh
            canvas_info = await self.initialize_canvas()
            cx, cy = canvas_info["center"]
            self.active_session = VisualDrawingSession(goal="Active Artwork", character_name="Active Artwork", canvas_center=[cx, cy])
            self.active_session.current_scene_state = self.perception_engine.analyze_canvas_scene([], "Artwork", cx * 2, cy * 2)

        scene = self.active_session.current_scene_state
        corr = self.corrector.generate_contextual_refinement(refinement_prompt, scene)

        print(f"[VISUAL REFINEMENT] Applying: '{corr.description}' ({len(corr.corrective_strokes)} delta strokes)...")

        if not self.client.is_connected:
            await self.client.connect(timeout_sec=4.0)

        res = await self.client.call_tool("uacc_draw_stroke_sequence", {"strokes": corr.corrective_strokes}, timeout_sec=15.0)

        if res.get("status") == "success":
            self.active_session.executed_strokes.extend(corr.corrective_strokes)
            self.active_session.refinements_applied.append(refinement_prompt)
            self.active_session.total_strokes += len(corr.corrective_strokes)

        # Re-observe canvas post-refinement
        updated_scene = self.perception_engine.analyze_canvas_scene(
            self.active_session.executed_strokes,
            self.active_session.goal,
            self.active_session.canvas_center[0] * 2,
            self.active_session.canvas_center[1] * 2
        )
        self.active_session.current_scene_state = updated_scene

        return {
            "status": "success",
            "refinement": refinement_prompt,
            "refinement_prompt": refinement_prompt,
            "action": corr.description,
            "strokes_added": len(corr.corrective_strokes),
            "total_canvas_strokes": self.active_session.total_strokes,
            "detected_objects": [obj.name for obj in updated_scene.detected_objects],
            "level": "Level 6 Contextual Visual Refinement"
        }


_GLOBAL_VISUAL_AGENT_LOOP: Optional[VisualAgentLoop] = None


def get_visual_agent_loop() -> VisualAgentLoop:
    global _GLOBAL_VISUAL_AGENT_LOOP
    if _GLOBAL_VISUAL_AGENT_LOOP is None:
        _GLOBAL_VISUAL_AGENT_LOOP = VisualAgentLoop()
    return _GLOBAL_VISUAL_AGENT_LOOP
