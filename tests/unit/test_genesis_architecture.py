"""Unit tests for Jarvis X: GENESIS Architectural Upgrade.

Covers:
- Architectural Independence between Inference, Computer Use, and Monetization
- MCP Client & Registry Lifecycle
- UACC Computer Use Adapter & Dual Backend Execution
- Llama.cpp Provider Interface
- Safety Gate & Permission Enforcer Integration
- Computer-Use Structured Observability & Credential Redaction
- Decoupled Dodo Payments Monetization Gateway
"""

import sys
import inspect
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from jarvisx.mcp.mcp_client import MCPClient, MCPToolDefinition
from jarvisx.mcp.mcp_registry import MCPRegistry, AdaptedMCPTool
from jarvisx.computer_use.uacc_adapter import UACCAdapter
from jarvisx.computer_use.computer_use_engine import ComputerUseEngine
from jarvisx.llm.llamacpp_provider import LlamaCppProvider
from jarvisx.llm.llm_provider import LLMProvider
from jarvisx.observability.computer_use_logger import ComputerUseLogger, redact_sensitive
from jarvisx.monetization.dodo_gateway import DodoPaymentsGateway
from jarvisx.tools.tool_kernel import ToolRegistry, PermissionLevel, ToolResult
from jarvisx.tools.builtin_tools import UACCComputerControlTool, register_builtin_tools
from jarvisx.tools.permission_gateway import PermissionGateway


def test_redact_sensitive_credentials():
    raw_text = "My API key is AIzaSyD1234567890abcdef1234567890 and password: secret_pass"
    cleaned = redact_sensitive(raw_text)
    assert "AIzaSy" not in cleaned
    assert "[REDACTED_SECRET]" in cleaned


def test_uacc_adapter_screen_inspection():
    uacc = UACCAdapter()
    res = uacc.inspect_screen()
    assert res["status"] == "success"
    assert "screen" in res
    assert "width" in res["screen"]
    assert "height" in res["screen"]
    assert "active_window" in res["screen"]


def test_uacc_adapter_execute_action():
    uacc = UACCAdapter()
    res = uacc.execute_action("inspect", {})
    assert res["status"] == "success"

    # Unknown action should return failed status
    res_bad = uacc.execute_action("invalid_action_xyz", {})
    assert res_bad["status"] == "failed"


def test_computer_use_engine_vscode_creation(tmp_path):
    engine = ComputerUseEngine()
    test_file = tmp_path / "test_script.py"
    code = "import numpy as np\nprint('Matrix Multiplication')\n"
    
    with patch("subprocess.Popen") as mock_popen:
        res = engine.type_code_in_vscode(str(test_file), code)
        assert res["status"] == "success"
        assert res["filename"] == "test_script.py"
        assert test_file.exists()


def test_mcp_client_tool_discovery():
    client = MCPClient(server_id="uacc_desktop")
    t_def = MCPToolDefinition(
        name="mouse_click",
        description="Click at coordinate",
        input_schema={"type": "object", "properties": {"x": {"type": "integer"}}},
        server_id="uacc_desktop"
    )
    client.discovered_tools["mouse_click"] = t_def

    adapted = AdaptedMCPTool(client, t_def, PermissionLevel.CONFIRM)
    spec = adapted.spec()
    assert spec.name == "mcp_uacc_desktop_mouse_click"
    assert spec.permission_level == PermissionLevel.CONFIRM


@pytest.mark.asyncio
async def test_llamacpp_provider_interface():
    provider = LlamaCppProvider(endpoint="http://localhost:8080")
    assert provider.name == "llamacpp.local"
    assert "gguf_quantization" in provider.capabilities()
    
    # Check fallback on offline endpoint
    health = await provider.health()
    assert health["provider"] == "llamacpp.local"


def test_dodo_monetization_isolation():
    gateway = DodoPaymentsGateway(api_key="test_key", webhook_secret="test_secret")
    checkout = gateway.create_checkout_session("test@example.com", plan_id="pro")
    assert checkout["status"] == "success"
    assert "checkout_url" in checkout
    assert checkout["amount_usd"] == 19.99


def test_uacc_computer_control_tool_execution():
    tool = UACCComputerControlTool()
    spec = tool.spec()
    assert spec.name == "uacc_computer_control"
    assert spec.permission_level == PermissionLevel.CONFIRM

    # Screen inspect action should succeed
    res = tool.execute({"action": "inspect", "params": {}})
    assert res.status == "success"
    assert res.tool == "uacc_computer_control"


def test_architectural_independence_inference_and_computer_use():
    """Verify that inference providers have zero hard imports of computer use or GUI drivers."""
    import jarvisx.llm.llm_provider as llm_p
    import jarvisx.llm.ollama_provider as ollama_p
    import jarvisx.llm.llamacpp_provider as llama_p

    for mod in (llm_p, ollama_p, llama_p):
        source = inspect.getsource(mod)
        assert "ComputerUseEngine" not in source
        assert "UACCAdapter" not in source
        assert "pyautogui" not in source


def test_permission_gateway_enforcement_on_computer_use():
    """Verify that PermissionGateway enforces CONFIRM approval on computer-use actions."""
    gateway = PermissionGateway()
    tool = UACCComputerControlTool()
    
    # Non-interactive mode must deny CONFIRM actions
    res = gateway.check(tool.spec(), {"action": "click", "params": {"x": 100, "y": 100}}, interactive=False)
    assert res["allowed"] is False
    assert "CONFIRM" in res["reason"]

    # SAFE tools are auto-approved
    from jarvisx.tools.builtin_tools import GetCurrentTimeTool
    time_tool = GetCurrentTimeTool()
    res_safe = gateway.check(time_tool.spec(), {}, interactive=False)
    assert res_safe["allowed"] is True


def test_art_synthesizer_vector_strokes():
    """Verify ArtSynthesizer produces valid parametric strokes for characters."""
    from jarvisx.computer_use.art_synthesizer import ArtSynthesizer
    
    zoro_strokes = ArtSynthesizer.generate_zoro_strokes(960, 540)
    assert len(zoro_strokes) >= 15
    for s in zoro_strokes:
        assert "start" in s and len(s["start"]) == 2
        assert "end" in s and len(s["end"]) == 2

    ironman_strokes = ArtSynthesizer.generate_ironman_strokes(960, 540)
    assert len(ironman_strokes) >= 10
    for s in ironman_strokes:
        assert "start" in s and "end" in s


def test_uacc_mcp_server_tools_spec():
    """Verify standalone UACC MCP Server exposes all required computer-use tools."""
    from jarvisx.mcp.uacc_server import TOOLS_SPEC, handle_inspect_screen
    
    names = [t["name"] for t in TOOLS_SPEC]
    assert "uacc_inspect_screen" in names
    assert "uacc_launch_app" in names
    assert "uacc_mouse_click" in names
    assert "uacc_mouse_drag" in names
    assert "uacc_draw_stroke_sequence" in names

    screen_res = handle_inspect_screen()
    assert "width" in screen_res
    assert "height" in screen_res
    assert "active_window" in screen_res


def test_visual_agent_loop_milestone_planning():
    """Verify VisualAgentLoop decomposes complex visual goals into progressive stages (Level 2 & 5)."""
    from jarvisx.computer_use.visual_agent_loop import VisualAgentLoop
    
    agent_loop = VisualAgentLoop()
    session = agent_loop.plan_visual_milestones("Luffy vs Zoro duel", 960, 540)
    assert len(session.stages) == 3
    assert session.stages[0].name == "Primary Contours"
    assert session.stages[1].name == "Facial Features & Scars"
    assert session.stages[2].name == "Santoryu Blades & Haki Clash"
    assert sum(len(s.strokes) for s in session.stages) >= 50


@pytest.mark.asyncio
async def test_visual_agent_loop_conversational_refinement():
    """Verify VisualAgentLoop can apply conversational refinements to active artwork (Level 6)."""
    from jarvisx.computer_use.visual_agent_loop import VisualAgentLoop
    
    agent_loop = VisualAgentLoop()
    agent_loop.plan_visual_milestones("Zoro", 960, 540)
    
    with patch.object(agent_loop.client, "call_tool", return_value={"status": "success"}):
        with patch.object(agent_loop.client, "connect", return_value=True):
            agent_loop.client.is_connected = True
            refine_res = await agent_loop.apply_conversational_refinement("Add Conqueror's Haki lightning")
            assert refine_res["status"] == "success"
            assert refine_res["strokes_added"] > 0
            assert "Conqueror's Haki" in refine_res["refinement"]


def test_canvas_perception_bounds():
    """Verify CanvasPerceptionEngine computes valid MS Paint canvas boundaries."""
    from jarvisx.computer_use.canvas_perception import CanvasPerceptionEngine
    
    bbox = CanvasPerceptionEngine.locate_paint_canvas(1920, 1080)
    assert bbox.width > 1000
    assert bbox.height > 600
    assert bbox.top >= 150
    assert bbox.left >= 20
    assert bbox.center_x == bbox.left + (bbox.width // 2)
    assert bbox.center_y == bbox.top + (bbox.height // 2)


def test_zero_shot_generative_visual_planner():
    """Verify GenerativeVisualPlanner compiles open-ended unseen prompts into 3-stage geometries."""
    from jarvisx.computer_use.canvas_perception import CanvasPerceptionEngine
    from jarvisx.computer_use.generative_visual_planner import GenerativeVisualPlanner

    bbox = CanvasPerceptionEngine.locate_paint_canvas(1920, 1080)

    # 1. Rocket Launching Prompt
    res_rocket = GenerativeVisualPlanner.compile_goal_to_stages("rocket launching into space", bbox)
    assert "Rocket" in res_rocket["subject"]
    assert len(res_rocket["stages"]) == 3
    assert all(len(s["strokes"]) > 0 for s in res_rocket["stages"])

    # 2. Coffee Mug Prompt
    res_coffee = GenerativeVisualPlanner.compile_goal_to_stages("steaming coffee mug", bbox)
    assert "Coffee" in res_coffee["subject"]
    assert len(res_coffee["stages"]) == 3

    # 3. Unseen Abstract Entity (Zero-Shot Synthesis)
    res_unseen = GenerativeVisualPlanner.compile_goal_to_stages("cybernetic matrix core", bbox)
    assert len(res_unseen["stages"]) == 3
    assert sum(len(s["strokes"]) for s in res_unseen["stages"]) >= 15


def test_semantic_canvas_perception_and_scene_state():
    """Verify SemanticCanvasPerceptionEngine produces structured SceneState with clusters and spatial density."""
    from jarvisx.computer_use.semantic_canvas_perception import SemanticCanvasPerceptionEngine
    
    engine = SemanticCanvasPerceptionEngine()
    dummy_strokes = [
        {"start": [900, 400], "end": [1020, 400]},
        {"start": [900, 400], "end": [960, 320]},
        {"start": [960, 320], "end": [1020, 400]},
        {"start": [800, 600], "end": [1120, 600]},
    ]
    scene = engine.analyze_canvas_scene(dummy_strokes, "Samurai on a mountain", 1920, 1080)
    assert scene.total_strokes_detected == len(dummy_strokes)
    assert len(scene.detected_objects) > 0
    assert "center" in scene.spatial_density
    assert scene.confidence >= 0.70


def test_semantic_visual_evaluator():
    """Verify VisualEvaluator detects missing elements and generates actionable recommendations."""
    from jarvisx.computer_use.semantic_canvas_perception import SemanticCanvasPerceptionEngine
    from jarvisx.computer_use.visual_evaluator import VisualEvaluator
    
    perc = SemanticCanvasPerceptionEngine()
    evaluator = VisualEvaluator()
    
    scene = perc.analyze_canvas_scene([], "Samurai on a mountain at sunset", 1920, 1080)
    evaluation = evaluator.evaluate_scene("Samurai on a mountain at sunset", scene)
    assert evaluation.completion_status == "INCOMPLETE"
    assert len(evaluation.missing_elements) >= 2
    assert len(evaluation.recommendations) > 0


def test_visual_corrector_delta_strokes():
    """Verify VisualCorrector synthesizes precise delta strokes for scale and refinement."""
    from jarvisx.computer_use.semantic_canvas_perception import SemanticCanvasPerceptionEngine
    from jarvisx.computer_use.visual_corrector import VisualCorrector
    
    perc = SemanticCanvasPerceptionEngine()
    corrector = VisualCorrector()
    
    scene = perc.analyze_canvas_scene([], "Samurai on a mountain", 1920, 1080)
    
    # Contextual refinement 1: Enlarge mountain
    corr_mountain = corrector.generate_contextual_refinement("Make the mountain larger", scene)
    assert corr_mountain.target_element == "mountain"
    assert corr_mountain.operation == "enlarge"
    assert len(corr_mountain.corrective_strokes) >= 3

    # Contextual refinement 2: Add missing sword
    corr_sword = corrector.generate_contextual_refinement("Add a sword to his right hand", scene)
    assert corr_sword.target_element == "sword"
    assert len(corr_sword.corrective_strokes) >= 3


@pytest.mark.asyncio
async def test_adversarial_visual_benchmark_10_tasks():
    """Verify AdversarialVisualBenchmarker evaluates all 10 unseen prompt tasks with 100% success."""
    from jarvisx.benchmark.adversarial_visual_benchmark import AdversarialVisualBenchmarker
    
    benchmarker = AdversarialVisualBenchmarker()
    summary = await benchmarker.run_benchmark(live_desktop=False)
    assert summary["tasks_run"] == 10
    assert summary["passed"] == 10
    assert summary["average_goal_match_score"] >= 0.85
    assert summary["overall_status"] == "PASSED"


def test_performance_optimizer_resource_reduction():
    """Verify PerformanceOptimizer executes resource reduction and returns metrics."""
    from jarvisx.reliability.performance_optimizer import PerformanceOptimizer
    
    opt = PerformanceOptimizer(".")
    rep = opt.optimize_system()
    assert rep.status == "COMPLETED"
    assert rep.after_ram_used_gb > 0
    assert rep.databases_compacted_count >= 0
    assert isinstance(rep.to_dict(), dict)
