"""Unit tests for PC Customizer Agent Mike (Layer 3 Operational Agent)."""

import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
import pytest

from jarvisx.agents.customizer_mike import MikeCustomizerAgent, PRESET_THEMES


@pytest.fixture
def agent():
    return MikeCustomizerAgent()


def test_agent_initialization(agent):
    """Verify Agent Mike identity, capabilities, and permissions."""
    assert agent.name == "Agent Mike"
    assert "lively_sync" in agent.capabilities
    assert "single_clock_enforcement" in agent.capabilities
    assert "dynamic_theme_synthesis" in agent.capabilities
    assert "negative_space_detection" in agent.capabilities
    status = agent.status()
    assert status["identity"] == "Agent Mike"


def test_franchise_theme_matching(agent):
    """Verify authentic franchise matching for known titles."""
    test_img = Image.new("RGB", (100, 100), color=(10, 10, 10))

    # One Piece
    theme_op = agent.synthesize_theme(test_img, ["luffy_gear5_moon.mp4", "one piece"])
    assert theme_op["is_preset"] is True
    assert theme_op["FontTitle"] == "ONE PIECE"

    # Naruto
    theme_naruto = agent.synthesize_theme(test_img, ["naruto-endless-sky.3840x2160.mp4"])
    assert theme_naruto["is_preset"] is True
    assert theme_naruto["FontTitle"] == "Ninja Naruto"

    # Batman
    theme_batman = agent.synthesize_theme(test_img, ["the_batman_vengeance_2022.jpg"])
    assert theme_batman["is_preset"] is True
    assert theme_batman["FontTitle"] == "BatmanForeverAlternate"

    # Minecraft
    theme_mc = agent.synthesize_theme(test_img, ["minecraft_shaders_landscape.mp4"])
    assert theme_mc["is_preset"] is True
    assert theme_mc["FontTitle"] == "Minecraft"

    # Ghost COD
    theme_cod = agent.synthesize_theme(test_img, ["simon_ghost_riley_modern_warfare.png"])
    assert theme_cod["is_preset"] is True
    assert theme_cod["FontTitle"] == "Agency FB"


def test_auto_synthesize_new_wallpaper(agent):
    """Verify dynamic AI/algorithmic synthesis on an unknown wallpaper."""
    # Create dark cyberpunk-style image with vibrant cyan and magenta
    img = Image.new("RGB", (200, 200), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 80, 80], fill=(0, 240, 255))
    draw.rectangle([100, 100, 180, 180], fill=(240, 60, 200))

    theme = agent.synthesize_theme(img, ["abstract_unknown_synth_city.mp4"])
    assert theme["is_preset"] is False
    assert "Dynamic Aesthetic" in theme["name"]
    # Check that WCAG contrast primary color is crisp white for dark background
    assert "255, 255, 255" in theme["ColorPrimary"]
    assert theme["StringEffect"] == "Shadow"


def test_negative_space_detection(agent):
    """Verify that negative space placer avoids high-clutter focal points."""
    # Create an image that is completely white/empty in UpperLeft, but very noisy in the center and bottom
    img = Image.new("RGB", (400, 250), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    # Draw complex subject/focal point in LowerRight & Center
    for i in range(150, 400, 10):
        draw.line([(i, 100), (i, 250)], fill=(255, 100, i % 255), width=3)
        draw.line([(150, i % 250), (400, i % 250)], fill=(100, 255, i % 255), width=3)

    placement = agent.calculate_negative_space(img)
    # UpperLeft has zero clutter, so it should be chosen
    assert placement["placement"] == "UpperLeft"
    assert placement["align"] == "Left"


def test_single_clock_ini_cleanup(agent, tmp_path, monkeypatch):
    """Verify that redundant competing skins are cleanly deactivated."""
    dummy_ini = tmp_path / "Rainmeter.ini"
    dummy_ini.write_text(
        "[Rainmeter]\n"
        "Logging=0\n\n"
        "[GhostMinimal\\Clock]\n"
        "Active=1\n\n"
        "[Mond\\Clock]\n"
        "Active=1\n\n"
        "[JarvisChameleonClock]\n"
        "Active=1\n",
        encoding="utf-8"
    )

    monkeypatch.setattr("jarvisx.agents.customizer_mike.RAINMETER_INI", dummy_ini)
    res = agent.enforce_single_clock()

    assert "GhostMinimal\\Clock" in res["unloaded_skins"]
    assert "Mond\\Clock" in res["unloaded_skins"]

    updated_content = dummy_ini.read_text(encoding="utf-8")
    assert "Active=0" in updated_content
    # Master clock remains untouched
    assert "[JarvisChameleonClock]\nActive=1" in updated_content


def test_agent_execute_task(agent):
    """Verify OperationalAgent execution routing and telemetry."""
    status_res = agent.execute({"action": "status"})
    assert status_res.get("agent") == "Agent Mike"
    assert agent._tasks_completed == 1
