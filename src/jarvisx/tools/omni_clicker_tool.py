"""OmniClicker Tool for Jarvis X Tool Kernel.

Exposes vision-based UI element finding, clicking, and typing via natural language
descriptions using local vision LLMs (Llama 3.2 Vision, LLaVA) and PyAutoGUI.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from jarvisx.tools.tool_kernel import (
    PermissionLevel,
    Tool,
    ToolResult,
    ToolSpec,
)
from jarvisx.vision.omni_clicker import OmniClicker

logger = logging.getLogger(__name__)

# Standalone Tool Schema Dict for LLM Tool Calling / Registration
OMNI_CLICKER_SCHEMA: Dict[str, Any] = {
    "name": "omni_clicker",
    "description": (
        "Vision-based UI control and clicker. Finds UI elements described in natural language "
        "(e.g., 'the blue subscribe button', 'search bar', 'settings gear icon') using a local "
        "vision model and clicks, double clicks, right clicks, hovers, or types into them."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["click", "find", "type", "double_click", "right_click", "hover", "drag"],
                "default": "click",
                "description": "Action to perform on target UI element: 'click', 'find', 'type', 'double_click', 'right_click', 'hover', or 'drag'.",
            },
            "description": {
                "type": "string",
                "description": "Natural language description of the target UI element (e.g. 'the blue subscribe button', 'search input field').",
            },
            "text": {
                "type": "string",
                "description": "Text to type into the element when action is 'type'.",
            },
            "button": {
                "type": "string",
                "enum": ["left", "right", "middle"],
                "default": "left",
                "description": "Mouse button to use for click actions.",
            },
            "clicks": {
                "type": "integer",
                "default": 1,
                "description": "Number of mouse clicks (1 for single, 2 for double).",
            },
            "clear_before": {
                "type": "boolean",
                "default": False,
                "description": "Whether to select all and clear existing text before typing.",
            },
            "press_enter": {
                "type": "boolean",
                "default": False,
                "description": "Whether to press Enter key after typing text.",
            },
            "model": {
                "type": "string",
                "description": "Optional vision LLM to use (e.g., 'llama3.2-vision', 'llava').",
            },
            "to_description": {
                "type": "string",
                "description": "Destination UI element description for 'drag' action.",
            },
        },
        "required": ["description"],
    },
    "permission_level": PermissionLevel.SAFE.value,
    "required_scope": "desktop.vision_control",
}

# Alias for general schema imports
TOOL_SCHEMA = OMNI_CLICKER_SCHEMA


class OmniClickerTool(Tool):
    """Tool wrapper around OmniClicker for the ToolExecutor pipeline."""

    def __init__(self, clicker: Optional[OmniClicker] = None) -> None:
        self.clicker = clicker or OmniClicker.get_instance()

    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=OMNI_CLICKER_SCHEMA["name"],
            description=OMNI_CLICKER_SCHEMA["description"],
            input_schema=OMNI_CLICKER_SCHEMA["input_schema"],
            permission_level=PermissionLevel.SAFE,
            required_scope="desktop.vision_control",
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute vision UI action using OmniClicker."""
        # Normalize argument aliases
        norm_args = dict(arguments)
        description = (
            norm_args.get("description")
            or norm_args.get("target")
            or norm_args.get("element")
            or norm_args.get("query")
            or norm_args.get("element_name")
            or ""
        )
        if not description:
            return ToolResult(
                status="failed",
                tool="omni_clicker",
                error="Missing required argument 'description' (target UI element description).",
            )

        action = str(norm_args.get("action", "click")).lower().strip()
        text = str(
            norm_args.get("text")
            or norm_args.get("content")
            or norm_args.get("value")
            or norm_args.get("input_text")
            or ""
        )
        button = str(norm_args.get("button", "left")).lower()
        clicks = int(norm_args.get("clicks", 1))
        clear_before = bool(norm_args.get("clear_before", False))
        press_enter = bool(norm_args.get("press_enter", False))
        model = norm_args.get("model")
        to_description = norm_args.get("to_description")

        try:
            if action == "find":
                res = self.clicker.find_element(description=description, model=model)
            elif action == "click":
                res = self.clicker.click_element(
                    description=description, button=button, clicks=clicks, model=model
                )
            elif action in ("type", "type_text", "type_into_element", "write"):
                if not text:
                    return ToolResult(
                        status="failed",
                        tool="omni_clicker",
                        error="Action 'type' requires non-empty 'text' argument.",
                    )
                res = self.clicker.type_into_element(
                    description=description,
                    text=text,
                    clear_before=clear_before,
                    press_enter=press_enter,
                    model=model,
                )
            elif action == "double_click":
                res = self.clicker.double_click_element(description=description, model=model)
            elif action == "right_click":
                res = self.clicker.right_click_element(description=description, model=model)
            elif action == "hover":
                res = self.clicker.hover_element(description=description, model=model)
            elif action == "drag":
                if not to_description:
                    return ToolResult(
                        status="failed",
                        tool="omni_clicker",
                        error="Action 'drag' requires 'to_description' argument.",
                    )
                res = self.clicker.drag_element(
                    from_description=description, to_description=to_description, model=model
                )
            else:
                return ToolResult(
                    status="failed",
                    tool="omni_clicker",
                    error=f"Unsupported action: '{action}'. Supported: click, find, type, double_click, right_click, hover, drag.",
                )

            status = "success" if res.get("status") == "SUCCESS" else "failed"
            error = res.get("error") if status == "failed" else None

            return ToolResult(
                status=status,
                tool="omni_clicker",
                result=res,
                error=error,
            )
        except Exception as e:
            logger.error(f"[OmniClickerTool] Execution error: {e}")
            return ToolResult(status="failed", tool="omni_clicker", error=str(e))

    def verify(self, arguments: Dict[str, Any], result: ToolResult) -> ToolResult:
        """Verify execution result."""
        verified = (
            result.status == "success"
            and isinstance(result.result, dict)
            and (result.result.get("found", True) or result.result.get("status") == "SUCCESS")
        )
        return ToolResult(
            status=result.status,
            tool=result.tool,
            result=result.result,
            verified=verified,
            error=result.error,
        )


def execute(arguments: Dict[str, Any]) -> ToolResult:
    """Direct functional entry point for ToolExecutor."""
    tool = OmniClickerTool()
    return tool.execute(arguments)
