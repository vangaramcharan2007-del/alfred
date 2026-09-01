"""
Unit tests for the Ultimate Spider-Man E-V Super Suite.
"""

import pytest
from jarvisx.agents.ev_super_engine import (
    EVSuperEngine,
    EVFlowGuardian,
    EVVoicePairProgrammer,
    EVSpiderSenseVision,
    EVMobileNeuralBridge,
    EVHolographicVisor,
)
from jarvisx.tools.tool_kernel import ToolRegistry
from jarvisx.tools.builtin_tools import (
    register_builtin_tools,
    EVFlowQuestTool,
    EVVoiceCodeTool,
    EVSpiderSenseVisionTool,
)


def test_ev_flow_guardian_context_and_quests():
    flow = EVFlowGuardian.get_instance()
    flow.remember_context("Writing Python attendance analyzer", "main.py")
    prompt = flow.recover_focus_prompt()
    assert "writing python attendance analyzer" in prompt.lower()
    assert "main.py" in prompt

    res = flow.complete_quest("q4")
    assert res["status"] == "success"
    assert res["total_xp"] > 450


def test_ev_voice_pair_programmer_code_synthesis():
    coder = EVVoicePairProgrammer.get_instance()
    res = coder.synthesize_code_from_voice("calculate student attendance and absences", "python")
    assert res["status"] == "success"
    assert "attendance" in res["generated_code"]
    assert "absences" in res["generated_code"]


def test_ev_voice_pair_programmer_error_interceptor():
    coder = EVVoicePairProgrammer.get_instance()
    fix = coder.intercept_and_fix_error("SyntaxError: unexpected EOF while parsing")
    assert fix["status"] == "success"
    assert "closing parenthesis" in fix["fix_applied"]


def test_ev_spider_sense_vision():
    vision = EVSpiderSenseVision.get_instance()
    res = vision.analyze_screen_snapshot()
    assert res["status"] == "success"
    assert "Spider-Sense is clear" in res["ev_speech"]


def test_ev_mobile_neural_bridge():
    mobile = EVMobileNeuralBridge.get_instance()
    res = mobile.send_mobile_update("Linux model training finished with 95% accuracy!", is_voice_note=True)
    assert res["status"] == "success"
    assert "88850 14923" in res["recipient"]


def test_ev_holographic_visor():
    visor = EVHolographicVisor.get_instance()
    res = visor.set_eye_mode("EXCITED")
    assert res["status"] == "success"
    assert res["eye_color"] == "#ffd700"


def test_ev_super_engine_singleton():
    engine = EVSuperEngine.get_instance()
    assert engine.flow is not None
    assert engine.pair_coder is not None
    assert engine.vision is not None
    assert engine.mobile is not None
    assert engine.visor is not None


def test_builtin_tools_ev_suite_registration():
    registry = ToolRegistry.get_instance()
    register_builtin_tools(registry)

    # 1. Flow Quest Tool
    q_tool = registry.get("manage_ev_flow_quest")
    assert q_tool is not None
    assert q_tool.execute({"action": "status"}).status == "success"

    # 2. Voice Code Tool
    c_tool = registry.get("generate_ev_voice_code")
    assert c_tool is not None
    assert c_tool.execute({"prompt": "fibonacci sequence"}).status == "success"

    # 3. Vision Tool
    v_tool = registry.get("scan_ev_spider_sense")
    assert v_tool is not None
    assert v_tool.execute({}).status == "success"
