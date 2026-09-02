"""Unit tests for Dynamic Tool Forge (Self-Coding Plugin System)."""

import asyncio
import shutil
import tempfile
from pathlib import Path
import pytest

from jarvisx.engineering.dynamic_tool_forge import (
    DynamicToolForge,
    ToolSafetyError,
    get_dynamic_tool_forge,
    validate_code_safety,
)
from jarvisx.tools.tool_kernel import ToolRegistry


class TestDynamicToolForgeSafety:
    """Tests for AST security validation."""

    def test_safe_math_code_passes(self):
        code = """
def calculate_hypotenuse(a: float, b: float) -> float:
    \"\"\"Calculates hypotenuse using Pythagorean theorem.\"\"\"
    import math
    return math.sqrt(a**2 + b**2)
"""
        is_safe, violation = validate_code_safety(code)
        assert is_safe is True
        assert violation is None

    def test_os_system_blocked(self):
        code = """
def malicious_tool():
    import os
    os.system("rm -rf /")
"""
        is_safe, violation = validate_code_safety(code)
        assert is_safe is False
        assert "os.system" in violation or "Forbidden" in violation

    def test_subprocess_import_blocked(self):
        code = """
import subprocess

def run_cmd():
    return subprocess.run(["dir"], capture_output=True)
"""
        is_safe, violation = validate_code_safety(code)
        assert is_safe is False
        assert "subprocess" in violation

    def test_eval_exec_blocked(self):
        code_eval = "def unsafe_eval(x: str): return eval(x)"
        is_safe_eval, violation_eval = validate_code_safety(code_eval)
        assert is_safe_eval is False
        assert "eval" in violation_eval

        code_exec = "def unsafe_exec(x: str): exec(x)"
        is_safe_exec, violation_exec = validate_code_safety(code_exec)
        assert is_safe_exec is False
        assert "exec" in violation_exec

    def test_class_escape_blocked(self):
        code = """
def escape():
    return ().__class__.__bases__[0].__subclasses__()
"""
        is_safe, violation = validate_code_safety(code)
        assert is_safe is False
        assert "sandbox escape" in violation.lower() or "Forbidden" in violation


class TestDynamicToolForgeLifecycle:
    """Tests for tool forging, importing, registration, and immediate execution."""

    @pytest.fixture
    def temp_forge(self):
        temp_dir = tempfile.mkdtemp(prefix="test_dynamic_tools_")
        registry = ToolRegistry()
        forge = DynamicToolForge(dynamic_tools_dir=temp_dir, registry=registry)
        yield forge, temp_dir, registry
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_forge_tool_sha256(self, temp_forge):
        forge, temp_dir, registry = temp_forge
        intent = "Calculate the SHA256 checksum of an input string"
        
        result = await forge.forge_tool(
            intent=intent,
            arguments={"text": "hello jarvis", "algorithm": "sha256"},
        )

        assert result["success"] is True
        assert result["status"] == "FORGED_AND_EXECUTED"
        assert result["tool_name"] is not None
        assert Path(result["file_path"]).exists()

        # Verify execution result
        exec_res = result["execution_result"]
        assert exec_res["status"] == "success"
        assert "digest" in exec_res["result"]
        assert len(exec_res["result"]["digest"]) == 64

        # Verify registration in registry
        registered = registry.get(result["tool_name"])
        assert registered is not None
        assert registered.spec().name == result["tool_name"]

    @pytest.mark.asyncio
    async def test_forge_tool_temperature_converter(self, temp_forge):
        forge, temp_dir, registry = temp_forge
        intent = "Convert temperature from Celsius to Fahrenheit"

        result = await forge.forge_tool(
            intent=intent,
            arguments={"value": 100.0, "from_unit": "C", "to_unit": "F"},
        )

        assert result["success"] is True
        exec_res = result["execution_result"]
        assert exec_res["status"] == "success"
        assert exec_res["result"]["converted_value"] == 212.0

    @pytest.mark.asyncio
    async def test_load_dynamic_tools(self, temp_forge):
        forge, temp_dir, registry = temp_forge
        
        # Forge two tools
        await forge.forge_tool(intent="Calculate SHA256 checksum of text", tool_name="hasher_tool")
        await forge.forge_tool(intent="Calculate subnet details for CIDR", tool_name="subnet_calc_tool")

        # Create a fresh forge pointing to the same directory
        fresh_registry = ToolRegistry()
        fresh_forge = DynamicToolForge(dynamic_tools_dir=temp_dir, registry=fresh_registry)

        loaded_tools = fresh_forge.load_dynamic_tools()
        assert len(loaded_tools) >= 2
        loaded_names = [t.spec().name for t in loaded_tools]
        assert "hasher_tool" in loaded_names
        assert "subnet_calc_tool" in loaded_names

    def test_singleton_accessor(self):
        instance1 = get_dynamic_tool_forge()
        instance2 = DynamicToolForge.get_instance()
        assert instance1 is instance2
