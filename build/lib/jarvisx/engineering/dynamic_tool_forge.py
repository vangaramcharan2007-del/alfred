"""
Dynamic Tool Forge — Self-Coding Plugin System for Jarvis X.
When no existing tool matches a user request, this module:
1. Generates Python code for a new tool via LLM
2. Validates it for safety
3. Saves it to src/jarvisx/tools/dynamic/
4. Dynamically imports and registers it
5. Executes it immediately
"""

import os
import re
import json
import logging
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional

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
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, code):
                logger.warning(f"[ToolForge] BLOCKED unsafe pattern: {pattern}")
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
