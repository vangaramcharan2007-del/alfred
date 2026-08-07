"""Unit Tests for Phase 93 Computer Use & Vision Layer."""

import pytest
import time
from pathlib import Path
from jarvisx.vision.ui_state import UIElement, UIState, Window
from jarvisx.vision.screen_capture import ScreenCaptureEngine
from jarvisx.vision.frame_buffer import FrameBuffer
from jarvisx.vision.ui_detector import UIDetector
from jarvisx.vision.element_matcher import UIElementMatcher
from jarvisx.vision.action_validator import ActionSafetyValidator
from jarvisx.vision.mouse_controller import MouseController
from jarvisx.vision.keyboard_controller import KeyboardController
from jarvisx.vision.visual_memory import VisualMemory
from jarvisx.vision.visual_reflection import VisualReflectionEngine
from jarvisx.vision.vision_engine import VisionEngine


def test_screen_capture_and_frame_buffer():
    capture = ScreenCaptureEngine(capture_dir="var/test_vision")
    frame1 = capture.capture_screenshot()
    assert frame1["status"] == "SUCCESS"
    assert Path(frame1["frame_path"]).exists()

    time.sleep(0.05)
    frame2 = capture.capture_screenshot()

    buffer = FrameBuffer()
    buffer.push_frame(frame1)
    buffer.push_frame(frame2)

    delta = buffer.compute_visual_delta(frame1, frame2)
    assert "delta_percentage" in delta
    assert delta["has_visual_change"] is True


def test_ui_detector_and_state():
    detector = UIDetector()
    state = detector.scan_ui_state()
    assert isinstance(state, UIState)
    assert len(state.elements) >= 3
    assert state.screen_resolution == (1920, 1080)


def test_element_matcher():
    state = UIState(
        windows=[Window("Visual Studio Code", (100, 100), (1280, 800), True)],
        elements=[
            UIElement("icon", "VS Code Launcher", 0.98, (20, 20, 60, 60), (40, 40)),
            UIElement("input", "Search Bar", 0.99, (80, 1040, 300, 1075), (190, 1057)),
        ]
    )

    matcher = UIElementMatcher()
    match = matcher.find_target_element("VS Code", state)
    assert match is not None
    assert match.center_coordinates == (40, 40)


def test_action_safety_validator():
    validator = ActionSafetyValidator(screen_bounds=(1920, 1080))

    # Valid within screen
    res_valid = validator.validate_mouse_action("click", (500, 500))
    assert res_valid["decision"] == "ALLOW"

    # Out of bounds blocked
    res_blocked = validator.validate_mouse_action("click", (2500, 3000))
    assert res_blocked["decision"] == "BLOCK"

    # Destructive button requires authorization
    del_el = UIElement("button", "Delete All Files", 0.99, (10, 10, 50, 50), (30, 30))
    res_danger = validator.validate_mouse_action("click", (30, 30), del_el)
    assert res_danger["decision"] == "ASK_USER"


def test_mouse_and_keyboard_controllers():
    mouse = MouseController(screen_bounds=(1920, 1080))
    res_move = mouse.move_to(300, 400)
    assert res_move["status"] == "SUCCESS"
    assert res_move["coordinates"] == (300, 400)

    res_click = mouse.click(300, 400)
    assert res_click["status"] == "SUCCESS"

    kb = KeyboardController()
    res_type = kb.type_text("Hello Jarvis")
    assert res_type["status"] == "SUCCESS"
    assert res_type["characters_typed"] == 12


def test_visual_reflection_and_recovery():
    reflection = VisualReflectionEngine()
    delta = {"has_visual_change": True, "delta_percentage": 12.0}
    post_state = UIState(windows=[Window("Notepad", (100, 100), (800, 600), True)])

    # Verified launch
    res_ver = reflection.verify_visual_action("open Notepad", "Notepad", delta, post_state)
    assert res_ver["verified"] is True
    assert res_ver["status"] == "SUCCESS"

    # Visual mismatch
    empty_state = UIState(windows=[])
    no_delta = {"has_visual_change": False, "delta_percentage": 0.0}
    res_mismatch = reflection.verify_visual_action("open Notepad", "Notepad", no_delta, empty_state)
    assert res_mismatch["verified"] is False
    assert res_mismatch["status"] == "VISUAL_MISMATCH"
    assert res_mismatch["needs_recovery"] is True


def test_vision_engine_end_to_end():
    engine = VisionEngine()
    desc = engine.describe_current_screen()
    assert desc["status"] == "SUCCESS"
    assert "resolution" in desc
    assert len(desc["elements_detected"]) >= 3

    task_res = engine.execute_visual_task("open Notepad")
    assert task_res["status"] == "SUCCESS"
    assert "coordinates_actuated" in task_res
