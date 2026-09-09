"""
Dynamic Tool Forge — Self-Coding Plugin System for Jarvis X.
When no existing tool matches a user request, this module:
1. Generates Python code for a new tool via LLM
2. Validates it for safety
3. Saves it to src/jarvisx/tools/dynamic/
4. Dynamically imports and registers it
5. Executes it immediately
"""

import ast
import os
import re
import json
import logging
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Safety blocklist — generated code must NOT contain these
BLOCKED_PATTERNS = [
    r'\bos\.system\b',
    r'\bsubprocess\b',
    r'\beval\b',
    r'\bexec\b',
    r'\b__import__\b',
    r'\bshutil\.rmtree\b',
    r'\bos\.remove\b',
    r'\bos\.unlink\b',
]

# Builtins that hand back arbitrary execution or the interpreter's guts.
BLOCKED_BUILTINS = frozenset({
    "eval", "exec", "compile", "__import__", "globals", "locals", "vars",
    "getattr", "setattr", "delattr", "breakpoint", "open", "input", "memoryview",
})

# Modules that reach the OS, the network, or the interpreter itself.
BLOCKED_MODULES = frozenset({
    "os", "subprocess", "shutil", "ctypes", "socket", "importlib", "sys",
    "builtins", "multiprocessing", "pty", "signal", "pathlib", "pickle",
    "marshal", "code", "codeop", "runpy", "platform",
})

# Attribute names that constitute the classic interpreter escape hatch.
# ().__class__.__bases__[0].__subclasses__() walks from any object to every
# class in the process, which includes subprocess.Popen and os._wrap_close.
ESCAPE_ATTRS = frozenset({
    "__class__", "__bases__", "__subclasses__", "__globals__", "__builtins__",
    "__mro__", "__code__", "__reduce__", "__import__", "__loader__",
    "__spec__", "__dict__", "__qualname__",
})


class ToolSafetyError(Exception):
    """Raised when generated tool code fails safety validation."""


def validate_code_safety(code: str) -> Tuple[bool, Optional[str]]:
    """Validate generated tool code before it is ever written to disk or run.

    Returns ``(True, None)`` when the code is acceptable, or
    ``(False, reason)`` describing the first violation found.

    This deliberately parses an AST rather than pattern-matching text. A regex
    blocklist cannot see the difference between a variable named ``execute``
    and the builtin ``exec``, and — far worse — it cannot see the dunder walk
    ``(().__class__.__bases__[0].__subclasses__())`` at all, because that
    contains none of the blocked words. That escape reaches every class in the
    process, including ``subprocess.Popen``, so a text-only check lets
    arbitrary command execution through a module whose entire purpose is to
    execute LLM-written code.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, f"SyntaxError: {exc.msg} (line {exc.lineno})"

    for node in ast.walk(tree):
        # Direct builtin calls: eval(...), exec(...), __import__(...), open(...)
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in BLOCKED_BUILTINS:
                return False, f"Forbidden builtin call: {func.id}()"
            # getattr(obj, "__globals__") style indirection
            if isinstance(func, ast.Attribute) and func.attr in ESCAPE_ATTRS:
                return False, f"Forbidden sandbox escape via attribute: {func.attr}"

        # Any dunder attribute access on the escape list, however it is used.
        if isinstance(node, ast.Attribute) and node.attr in ESCAPE_ATTRS:
            return False, (
                f"Forbidden sandbox escape: access to '{node.attr}' "
                f"allows walking to arbitrary classes"
            )

        # Imports, in both `import x` and `from x import y` form.
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in BLOCKED_MODULES:
                    return False, f"Forbidden module import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root in BLOCKED_MODULES:
                    return False, f"Forbidden module import: {node.module}"

        # os.system / shutil.rmtree style calls survive as a second line of
        # defence for anything the name checks above did not already catch.
        if isinstance(node, ast.Attribute):
            dotted = _dotted(node)
            for pattern in BLOCKED_PATTERNS:
                if re.search(pattern, dotted):
                    return False, f"Forbidden pattern: {dotted}"

    # Fall back to the raw-text scan for constructs the AST walk is not
    # structured to notice (string-built code, comments smuggling payloads).
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, code):
            return False, f"Forbidden pattern: {pattern}"

    return True, None


def _dotted(node: ast.AST) -> str:
    """Render an attribute chain back to dotted source text, e.g. os.system."""
    parts: List[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def get_dynamic_tool_forge() -> "DynamicToolForge":
    """Return the process-wide DynamicToolForge, creating it if needed.

    This is the accessor ``jarvisx.engineering`` advertises in ``__all__``;
    without it ``from jarvisx.engineering import get_dynamic_tool_forge``
    raised ImportError, because the package's ``__getattr__`` imported the
    name from here and the name did not exist.
    """
    return DynamicToolForge.get_instance()

DYNAMIC_TOOLS_DIR = Path(__file__).parent.parent / "tools" / "dynamic"


class DynamicToolForge:
    """Autonomous tool generator that writes, validates, and loads new tools at runtime."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "DynamicToolForge":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        DYNAMIC_TOOLS_DIR.mkdir(parents=True, exist_ok=True)
        init_file = DYNAMIC_TOOLS_DIR / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding="utf-8")
        self._loaded_tools: Dict[str, Dict[str, Any]] = {}
        self.load_dynamic_tools()

    def _validate_code(self, code: str) -> bool:
        """Check generated code against safety blocklist."""
        is_safe, violation = validate_code_safety(code)
        if not is_safe:
            logger.warning(f"[ToolForge] BLOCKED unsafe code: {violation}")
            return False
        return True

    def _generate_tool_code(self, intent: str, existing_tools: List[str]) -> Optional[Dict[str, str]]:
        """Ask LLM to generate a new tool's Python code and schema."""
        try:
            import ollama
        except ImportError:
            logger.error("[ToolForge] ollama not installed")
            return None

        prompt = f"""You are a Python tool generator for an AI assistant called Jarvis X.

The user wants to do something that none of the existing tools can handle.
Existing tools: {', '.join(existing_tools)}

User intent: "{intent}"

Generate a NEW Python tool. Output ONLY a JSON object with these keys:
- "tool_name": snake_case name (e.g. "convert_currency")
- "description": one-line description
- "parameters": dict of param_name -> param_description
- "code": the full Python function code as a string. The function must be named `execute(args: dict) -> dict` and return a dict with "status" and "result" keys.

Example output:
{{
  "tool_name": "convert_currency",
  "description": "Convert between currencies using exchange rates",
  "parameters": {{"from_currency": "Source currency code", "to_currency": "Target currency code", "amount": "Amount to convert"}},
  "code": "import requests\\n\\ndef execute(args: dict) -> dict:\\n    # implementation\\n    return {{\\"status\\": \\"success\\", \\"result\\": converted}}"
}}

IMPORTANT: Do NOT use os.system, subprocess, eval, exec, or any destructive operations.
Output ONLY the JSON object, no markdown."""

        try:
            res = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages=[{"role": "user", "content": prompt}]
            )
            text = res["message"]["content"].strip()

            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            return json.loads(text)
        except Exception as e:
            logger.error(f"[ToolForge] LLM generation failed: {e}")
            return None

    async def forge_tool(self, intent: str, existing_tools: List[str]) -> Dict[str, Any]:
        """Generate, validate, save, load, and execute a new tool."""
        logger.info(f"[ToolForge] Forging new tool for: {intent}")

        spec = self._generate_tool_code(intent, existing_tools)
        if not spec:
            return {"status": "failed", "error": "LLM failed to generate tool code"}

        tool_name = spec.get("tool_name", "unknown_tool")
        code = spec.get("code", "")

        # Safety check
        if not self._validate_code(code):
            return {"status": "blocked", "error": "Generated code contains unsafe patterns"}

        # Save to file
        tool_file = DYNAMIC_TOOLS_DIR / f"{tool_name}.py"
        tool_file.write_text(code, encoding="utf-8")

        # Save schema
        schema = {
            "name": tool_name,
            "description": spec.get("description", "Dynamically generated tool"),
            "parameters": spec.get("parameters", {}),
        }
        schema_file = DYNAMIC_TOOLS_DIR / f"{tool_name}.json"
        schema_file.write_text(json.dumps(schema, indent=2), encoding="utf-8")

        # Dynamic import
        try:
            spec_obj = importlib.util.spec_from_file_location(tool_name, str(tool_file))
            module = importlib.util.module_from_spec(spec_obj)
            spec_obj.loader.exec_module(module)

            if hasattr(module, "execute"):
                self._loaded_tools[tool_name] = {
                    "schema": schema,
                    "execute": module.execute,
                    "file": str(tool_file),
                }
                logger.info(f"[ToolForge] Successfully forged and loaded: {tool_name}")
                return {
                    "status": "success",
                    "tool_name": tool_name,
                    "description": schema["description"],
                    "file": str(tool_file),
                }
            else:
                return {"status": "failed", "error": "Generated code missing execute() function"}
        except Exception as e:
            logger.error(f"[ToolForge] Import failed: {e}")
            return {"status": "failed", "error": str(e)}

    def load_dynamic_tools(self) -> List[Dict[str, Any]]:
        """Load all previously forged tools from disk."""
        schemas = []
        for schema_file in DYNAMIC_TOOLS_DIR.glob("*.json"):
            try:
                schema = json.loads(schema_file.read_text(encoding="utf-8"))
                tool_name = schema["name"]
                tool_file = DYNAMIC_TOOLS_DIR / f"{tool_name}.py"

                if tool_file.exists():
                    spec_obj = importlib.util.spec_from_file_location(tool_name, str(tool_file))
                    module = importlib.util.module_from_spec(spec_obj)
                    spec_obj.loader.exec_module(module)

                    if hasattr(module, "execute"):
                        self._loaded_tools[tool_name] = {
                            "schema": schema,
                            "execute": module.execute,
                            "file": str(tool_file),
                        }
                        schemas.append(schema)
            except Exception as e:
                logger.warning(f"[ToolForge] Failed to load {schema_file}: {e}")
        return schemas

    def get_loaded_tools(self) -> Dict[str, Dict[str, Any]]:
        return self._loaded_tools

    def execute_tool(self, tool_name: str, args: dict) -> Dict[str, Any]:
        """Execute a dynamically loaded tool by name."""
        tool = self._loaded_tools.get(tool_name)
        if not tool:
            return {"status": "failed", "error": f"Tool '{tool_name}' not loaded"}
        try:
            return tool["execute"](args)
        except Exception as e:
            return {"status": "failed", "error": str(e)}
