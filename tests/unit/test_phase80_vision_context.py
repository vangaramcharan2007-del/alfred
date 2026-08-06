"""Unit and Integration Tests for Phase 80: Multi-Modal Screen & Vision Context Engine.

Tests ScreenContextEngine, ContextSynthesizer, and kernel vision context objectives.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.vision import ScreenContextEngine, ContextSynthesizer


def test_screen_context_engine_capture_and_classification():
    """Verify ScreenContextEngine captures active window info and categorizes context."""
    engine = ScreenContextEngine()

    res = engine.capture_active_context()
    assert res["status"] == "CAPTURED"
    assert "context_category" in res
    assert "active_window" in res


def test_context_synthesizer_assistance_generation():
    """Verify ContextSynthesizer generates contextual assistance based on active screen."""
    kernel = PersonalOSKernel()
    synthesizer = ContextSynthesizer(context_engine=kernel.screen_context)

    res = synthesizer.generate_contextual_assistance(os_kernel=kernel)
    assert res["status"] == "SYNTHESIZED"
    assert "assistance" in res
    assert "recommendation" in res["assistance"]


def test_kernel_objective_routing_phase80():
    """Verify PersonalOSKernel routes screen context and contextual assistance objectives."""
    kernel = PersonalOSKernel()

    ctx_res = kernel.execute_objective("screen context")
    assert ctx_res["status"] == "CAPTURED"

    ast_res = kernel.execute_objective("contextual assistance")
    assert ast_res["status"] == "SYNTHESIZED"
