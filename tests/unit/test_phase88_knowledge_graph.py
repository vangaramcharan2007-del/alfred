"""Unit and Integration Tests for Phase 88: Autonomous Personal Knowledge Graph & Multi-Hop Causal Reasoning Engine.

Tests KnowledgeGraphEngine node/edge graph construction, multi-hop derivation, and kernel objectives.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from jarvisx.kernel.personal_os import PersonalOSKernel
from jarvisx.memory import KnowledgeGraphEngine


def test_knowledge_graph_engine_causal_derivation():
    """Verify KnowledgeGraphEngine constructs graph nodes, edges, and traverses multi-hop causal paths."""
    engine = KnowledgeGraphEngine()

    res = engine.infer_causal_derivation("Why did study progress accelerate?")
    assert res["status"] == "COMPLETED"
    assert res["graph_nodes"] >= 4
    assert res["graph_edges"] >= 3
    assert "traversal_path" in res
    assert res["graph_hspw"] >= 14.5


def test_kernel_objective_routing_phase88():
    """Verify PersonalOSKernel routes knowledge graph causal reasoning objectives."""
    kernel = PersonalOSKernel()

    res = kernel.execute_objective("infer causality")
    assert res["status"] == "COMPLETED"
    assert "derivation" in res
