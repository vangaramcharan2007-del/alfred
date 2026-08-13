"""Unit tests for NPUAccelerator and thermal cooling manager in Jarvis X."""

import pytest
from jarvisx.hardware.npu_accelerator import NPUAccelerator, get_npu_accelerator


def test_npu_accelerator_detection():
    npu = NPUAccelerator()
    health = npu.get_system_health()
    assert "hardware" in health
    assert health["ram_total_gb"] > 0
    assert "power_profile" in health
    assert health["power_profile"] in ("ECO", "BALANCED", "PERFORMANCE")


def test_npu_options_and_cooling():
    npu = NPUAccelerator()
    npu.power_profile = "ECO"
    opts = npu.get_recommended_ollama_options("qwen2.5-coder:1.5b")
    assert opts["num_thread"] <= 4
    assert opts["keep_alive"] == "30s"

    cooling_res = npu.enforce_memory_cooling()
    assert cooling_res["status"] == "COOLED"
