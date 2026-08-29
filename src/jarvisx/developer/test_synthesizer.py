"""
Autonomous Test Suite Synthesizer for Jarvis X.
Generates comprehensive unit tests for arbitrary source code modules using LLM code generation.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from jarvisx.mesh.mesh_router import MeshRouter, get_mesh_router


@dataclass
class GeneratedTestSuite:
    module_name: str
    test_code: str
    test_count: int
    duration_ms: float


class AutonomousTestSynthesizer:
    """Generates unit tests for Python modules and functions."""

    def __init__(self, mesh_router: Optional[MeshRouter] = None):
        self.router = mesh_router or get_mesh_router()

    def generate_tests_for_code(self, source_code: str, module_name: str = "target_module") -> GeneratedTestSuite:
        """Synthesizes a complete unit test suite for the given code snippet."""
        start_t = time.time()
        prompt = (
            f"You are an expert Test Engineer. Generate a complete, standalone Python unittest/test suite for this code:\n\n"
            f"```python\n{source_code}\n```\n\n"
            f"Requirements:\n"
            f"1. Include test assertions for standard cases, edge cases (empty inputs, negative values, boundary values).\n"
            f"2. Make it a self-contained executable script with assert statements or unittest.main().\n"
            f"3. Return ONLY valid Python code enclosed in ```python ... ```."
        )

        res = self.router.dispatch_intent(prompt, preferred_model="qwen2.5-coder:1.5b")
        raw_output = res.get("response", "")

        # Extract code block
        m = re.search(r"```(?:python)?\s*(.*?)\s*```", raw_output, re.DOTALL)
        if m:
            test_code = m.group(1).strip()
        else:
            test_code = raw_output.strip()

        # Count assertions or test functions
        test_count = max(1, len(re.findall(r"def test_|assert ", test_code)))
        dur = round((time.time() - start_t) * 1000, 2)

        return GeneratedTestSuite(
            module_name=module_name,
            test_code=test_code,
            test_count=test_count,
            duration_ms=dur,
        )
