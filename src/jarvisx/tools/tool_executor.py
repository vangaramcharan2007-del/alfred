"""Tool Executor — orchestrates Registry → Validation → Permission → Execute → Verify pipeline."""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, Optional

from jarvisx.tools.tool_kernel import ToolRegistry, ToolResult
from jarvisx.tools.permission_gateway import PermissionGateway

logger = logging.getLogger("jarvisx.tool_executor")


class ToolExecutor:
    """Safe, validated tool execution pipeline."""

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        gateway: Optional[PermissionGateway] = None,
    ) -> None:
        self.registry = registry or ToolRegistry.get_instance()
        self.gateway = gateway or PermissionGateway()

    def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        interactive: bool = True,
    ) -> ToolResult:
        """Full pipeline: lookup → validate → permission → execute → verify."""
        t0 = time.perf_counter()

        # 1. Registry lookup
        tool = self.registry.get(tool_name)
        if tool is None:
            logger.warning(f"[ToolExecutor] Rejected unknown tool: '{tool_name}'")
            return ToolResult(status="failed", tool=tool_name, error=f"Unknown tool: '{tool_name}'")

        spec = tool.spec()

        # 2. Argument validation
        validation = self.registry.validate(tool_name, arguments)
        if not validation.get("valid"):
            logger.warning(f"[ToolExecutor] Argument validation failed for '{tool_name}': {validation.get('error')}")
            return ToolResult(status="failed", tool=tool_name, error=validation.get("error", "Invalid arguments"))

        # 3. Permission check
        perm = self.gateway.check(spec, arguments, interactive=interactive)
        if not perm.get("allowed"):
            logger.info(f"[ToolExecutor] Permission denied for '{tool_name}': {perm.get('reason')}")
            return ToolResult(status="failed", tool=tool_name, error=perm.get("reason", "Permission denied"))

        # 4. Execute
        try:
            result = tool.execute(arguments)
        except Exception as e:
            logger.error(f"[ToolExecutor] Exception in '{tool_name}': {e}")
            return ToolResult(status="failed", tool=tool_name, error=f"Execution error: {e}")

        # 5. Verify
        try:
            verified_result = tool.verify(arguments, result)
        except Exception as e:
            logger.error(f"[ToolExecutor] Verification error in '{tool_name}': {e}")
            verified_result = ToolResult(
                status=result.status, tool=tool_name,
                result=result.result, verified=False, error=f"Verification error: {e}",
            )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        logger.info(f"[ToolExecutor] {tool_name} completed in {elapsed_ms}ms — verified={verified_result.verified}")

        return verified_result

    @staticmethod
    def parse_tool_call(llm_response: str) -> Optional[Dict[str, Any]]:
        """Extract structured tool call from LLM response text.

        Looks for JSON with: {"type": "tool_call", "tool": "...", "arguments": {...}}
        Returns None if the response is a normal conversational answer.
        """
        text = llm_response.strip()
        decoder = json.JSONDecoder()

        # Scan for JSON objects starting from each '{'
        idx = 0
        while idx < len(text):
            start = text.find("{", idx)
            if start == -1:
                break
            try:
                parsed, _ = decoder.raw_decode(text[start:])
                if (
                    isinstance(parsed, dict)
                    and parsed.get("type") == "tool_call"
                    and isinstance(parsed.get("tool"), str)
                    and bool(parsed.get("tool"))
                    and isinstance(parsed.get("arguments"), dict)
                ):
                    return parsed
                idx = start + 1
            except (json.JSONDecodeError, ValueError):
                idx = start + 1

        return None

    def build_tool_system_prompt(self) -> str:
        """Build system prompt fragment describing available tools for LLM."""
        schemas = self.registry.get_schemas_for_llm()
        if not schemas:
            return ""

        tools_desc = json.dumps(schemas, indent=2)
        return (
            "You have access to the following tools. "
            "If the user's request requires a tool, respond with ONLY ONE JSON tool call at a time:\n"
            '{"type": "tool_call", "tool": "<tool_name>", "arguments": {<args>}}\n\n'
            "If the request is a normal conversation or question, respond naturally with text.\n"
            "Do NOT output multiple tool calls at once. Execute one step, and you will receive the result before making the next decision.\n\n"
            f"Available tools:\n{tools_desc}\n"
        )

