"""Unit and Integration Tests for Phase 86: Zero-Latency Offline Edge Model Acceleration & Local Quantization Manager.

Tests EdgeQuantizationManager hardware capacity inspection, model allocation, latency targets, and kernel objectives.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.runtime import EdgeQuantizationManager


def test_edge_quantization_manager_allocation():
    """Verify EdgeQuantizationManager inspects hardware capacity and allocates Q4_K_M model weights."""
    manager = EdgeQuantizationManager()
    hw = manager.inspect_hardware_capacity()
    assert "cpu_threads" in hw
    assert "vram_allocated_mb" in hw

    res = manager.allocate_model_quantization(model_name="mistral-7b", preferred_precision="Q4_K_M")
    assert res["status"] == "ALLOCATED"
    assert res["estimated_latency_ms"] < 50.0
    assert res["cloud_compute_cost"] == "$0.00"
    assert res["edge_hspw"] >= 18.5


def test_kernel_objective_routing_phase86():
    """Verify PersonalOSKernel routes edge model quantization objectives."""
    kernel = PersonalOSKernel()

    res = kernel.execute_objective("edge model", model="phi-3", precision="Q4_K_M")
    assert res["status"] == "ALLOCATED"
    assert res["estimated_latency_ms"] < 50.0
