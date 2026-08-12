"""Tool & Action Execution Kernel — Core Abstractions.

Provides the typed tool contract, permission levels, structured results,
and central registry for safe LLM-driven tool execution.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.tool_kernel")


class PermissionLevel(str, Enum):
    """Tool permission classification."""
    SAFE = "SAFE"              # Auto-approved, no user interaction
    CONFIRM = "CONFIRM"        # Requires explicit user confirmation
    RESTRICTED = "RESTRICTED"  # Blocked by default


@dataclass(frozen=True)
class ToolSpec:
    """Typed specification for a registered tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]          # JSON Schema for arguments
    permission_level: PermissionLevel
    required_scope: Optional[str] = None  # Maps to PermissionScope value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "permission_level": self.permission_level.value,
        }


@dataclass
class ToolResult:
    """Structured result from tool execution."""
    status: str          # "success" or "failed"
    tool: str            # tool name
    result: Any = None   # execution output
    verified: bool = False
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "status": self.status,
            "tool": self.tool,
            "result": self.result,
            "verified": self.verified,
        }
        if self.error:
            d["error"] = self.error
        return d


class Tool(ABC):
    """Abstract base class for all executable tools."""

    @abstractmethod
    def spec(self) -> ToolSpec:
        """Return the typed specification for this tool."""
        ...

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the tool with validated arguments."""
        ...

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        """Verify execution outcome. Override for tool-specific verification."""
        return ToolResult(
            status=result.status,
            tool=result.tool,
            result=result.result,
            verified=result.status == "success",
            error=result.error,
        )


class ToolRegistry:
    """Central registry — the only route from tool name to executable implementation."""

    _instance: Optional[ToolRegistry] = None

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    @classmethod
    def get_instance(cls) -> ToolRegistry:
        if cls._instance is None:
            cls._instance = ToolRegistry()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def register(self, tool: Tool) -> None:
        spec = tool.spec()
        self._tools[spec.name] = tool
        logger.info(f"[ToolRegistry] Registered: {spec.name} ({spec.permission_level.value})")

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolSpec]:
        return [t.spec() for t in self._tools.values()]

    def validate(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool name exists and arguments match the input schema."""
        tool = self._tools.get(name)
        if tool is None:
            return {"valid": False, "error": f"Unknown tool: '{name}'"}

        schema = tool.spec().input_schema
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Check required fields
        for req in required:
            if req not in arguments:
                return {"valid": False, "error": f"Missing required argument: '{req}'"}

        # Check types
        for key, value in arguments.items():
            if key not in properties:
                return {"valid": False, "error": f"Unknown argument: '{key}'"}
            expected_type = properties[key].get("type", "string")
            type_map = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "object": dict, "array": list}
            expected = type_map.get(expected_type, str)
            if not isinstance(value, expected):
                return {"valid": False, "error": f"Argument '{key}' must be {expected_type}, got {type(value).__name__}"}

        return {"valid": True}

    def get_schemas_for_llm(self) -> List[Dict[str, Any]]:
        """Return tool schemas formatted for LLM system prompt injection."""
        return [t.spec().to_dict() for t in self._tools.values()]
