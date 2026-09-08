"""Schema-driven tool registry for the agentic harness.

Reuses the project's existing :mod:`jarvisx.tools.tool_kernel` permission model
(``SAFE`` / ``CONFIRM`` / ``RESTRICTED``) so the harness inherits Alfred's
security policy instead of inventing a parallel one, and adds:

* a decorator API for registering plain Python functions as tools,
* real JSON-Schema subset validation *before* execution,
* OpenAI function-calling schema export for the model layer.
"""

from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, get_type_hints

from jarvisx.agentic.types import Observation, ToolCall
from jarvisx.tools.tool_kernel import PermissionLevel

logger = logging.getLogger("jarvisx.agentic.registry")


@dataclass(frozen=True)
class AgentTool:
    """A callable exposed to the model, with its schema and permission tier."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    permission: PermissionLevel
    handler: Callable[..., Any]
    tags: tuple = ()

    def to_openai_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema or {"type": "object", "properties": {}},
            },
        }

    def to_flat_schema(self) -> Dict[str, Any]:
        """Schema shape used by backends without native tool calling."""
        return {
            "name": self.name,
            "description": self.description,
            "permission": self.permission.value,
            "parameters": self.input_schema or {"type": "object", "properties": {}},
        }


class ToolValidationError(ValueError):
    """Raised when model-supplied arguments do not satisfy a tool's schema."""


class UnknownTool(KeyError):
    """Raised when the model asks for a tool that is not registered."""


class ToolDenied(PermissionError):
    """Raised when policy refuses a tool call."""


# --------------------------------------------------------------------------- #
# JSON-Schema subset validation
# --------------------------------------------------------------------------- #

_TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
    "null": type(None),
}


def validate_arguments(schema: Dict[str, Any], arguments: Dict[str, Any]) -> None:
    """Validate `arguments` against the object-schema subset we support.

    Raises :class:`ToolValidationError` on the first problem found.
    """
    properties: Dict[str, Any] = schema.get("properties", {}) or {}
    required: Sequence[str] = schema.get("required", []) or ()

    for key in required:
        if key not in arguments or arguments[key] is None:
            raise ToolValidationError(f"missing required argument '{key}'")

    additional = schema.get("additionalProperties", False)
    for key, value in arguments.items():
        if key not in properties:
            if additional:
                continue
            raise ToolValidationError(
                f"unexpected argument '{key}' (allowed: {sorted(properties) or 'none'})"
            )
        spec = properties[key]
        expected = spec.get("type")
        if expected and not _matches_type(value, expected):
            raise ToolValidationError(
                f"argument '{key}' must be {expected}, got {type(value).__name__}"
            )
        enum = spec.get("enum")
        if enum and value not in enum:
            raise ToolValidationError(f"argument '{key}' must be one of {list(enum)}")
        if expected == "array" and isinstance(value, list):
            item_type = (spec.get("items") or {}).get("type")
            if item_type:
                for index, item in enumerate(value):
                    if not _matches_type(item, item_type):
                        raise ToolValidationError(
                            f"argument '{key}[{index}]' must be {item_type}"
                        )


def _matches_type(value: Any, expected: Any) -> bool:
    if isinstance(expected, list):
        return any(_matches_type(value, single) for single in expected)
    python_type = _TYPE_MAP.get(expected)
    if python_type is None:
        return True
    if python_type is int and isinstance(value, bool):
        return False
    if python_type is not bool and isinstance(value, bool):
        return expected == "boolean"
    return isinstance(value, python_type)


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #


class AgentToolRegistry:
    """Central registry: the only route from tool name to executable handler."""

    def __init__(self) -> None:
        self._tools: Dict[str, AgentTool] = {}

    # -- registration ------------------------------------------------------ #

    def register(
        self,
        handler: Callable[..., Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        permission: PermissionLevel = PermissionLevel.SAFE,
        tags: Iterable[str] = (),
    ) -> AgentTool:
        tool = AgentTool(
            name=name or handler.__name__,
            description=(
                description
                or inspect.getdoc(handler)
                or f"Execute {handler.__name__}"
            ).strip().splitlines()[0],
            input_schema=input_schema or _schema_from_signature(handler),
            permission=permission,
            handler=handler,
            tags=tuple(tags),
        )
        self._tools[tool.name] = tool
        logger.debug("registered tool %s (%s)", tool.name, tool.permission.value)
        return tool

    def tool(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        permission: PermissionLevel = PermissionLevel.SAFE,
        tags: Iterable[str] = (),
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator form of :meth:`register`."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.register(
                func,
                name=name,
                description=description,
                input_schema=input_schema,
                permission=permission,
                tags=tags,
            )
            return func

        return decorator

    # -- introspection ----------------------------------------------------- #

    def get(self, name: str) -> AgentTool:
        try:
            return self._tools[name]
        except KeyError:
            raise UnknownTool(
                f"unknown tool '{name}' (registered: {self.names() or 'none'})"
            ) from None

    def names(self) -> List[str]:
        return sorted(self._tools)

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: object) -> bool:
        return name in self._tools

    def openai_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_openai_schema() for tool in self._tools.values()]

    def flat_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_flat_schema() for tool in self._tools.values()]

    # -- execution --------------------------------------------------------- #

    def invoke(
        self,
        call: ToolCall,
        approve: Optional[Callable[[AgentTool, Dict[str, Any]], bool]] = None,
    ) -> Observation:
        """Validate, authorize and execute one tool call.

        Never raises for model-side mistakes: validation failures, unknown
        tools and policy denials all come back as :class:`Observation` objects
        so the model can read the error and self-correct on the next step.
        """
        import time

        started = time.perf_counter()
        try:
            tool = self.get(call.name)
        except UnknownTool as exc:
            return Observation(
                tool=call.name,
                call_id=call.id,
                ok=False,
                error=str(exc),
                duration_ms=_ms(started),
            )

        try:
            validate_arguments(tool.input_schema or {}, call.arguments)
        except ToolValidationError as exc:
            return Observation(
                tool=call.name,
                call_id=call.id,
                ok=False,
                error=f"schema violation: {exc}",
                duration_ms=_ms(started),
            )

        if tool.permission is PermissionLevel.RESTRICTED:
            return Observation(
                tool=call.name,
                call_id=call.id,
                ok=False,
                denied=True,
                error=f"'{call.name}' is RESTRICTED and blocked by default policy",
                duration_ms=_ms(started),
            )

        if tool.permission is PermissionLevel.CONFIRM:
            approved = bool(approve(tool, call.arguments)) if approve else False
            if not approved:
                return Observation(
                    tool=call.name,
                    call_id=call.id,
                    ok=False,
                    denied=True,
                    error=f"'{call.name}' requires confirmation that was not granted",
                    duration_ms=_ms(started),
                )

        try:
            output = tool.handler(**call.arguments)
        except Exception as exc:  # noqa: BLE001 - fed back to the model
            logger.warning("tool %s raised: %s", call.name, exc)
            return Observation(
                tool=call.name,
                call_id=call.id,
                ok=False,
                error=f"{type(exc).__name__}: {exc}",
                duration_ms=_ms(started),
            )

        return Observation(
            tool=call.name,
            call_id=call.id,
            ok=True,
            output=output,
            duration_ms=_ms(started),
        )


def _schema_from_signature(handler: Callable[..., Any]) -> Dict[str, Any]:
    """Derive a best-effort JSON schema from a Python signature.

    Annotations are resolved through :func:`typing.get_type_hints` first: under
    ``from __future__ import annotations`` the signature only exposes strings
    like ``"bool"``, which would otherwise silently degrade to ``"string"``.
    """
    hints = _resolve_hints(handler)
    signature = inspect.signature(handler)
    properties: Dict[str, Any] = {}
    required: List[str] = []
    for param in signature.parameters.values():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        annotation = hints.get(param.name, param.annotation)
        properties[param.name] = {"type": _json_type(annotation)}
        if param.default is inspect.Parameter.empty:
            required.append(param.name)
    return {"type": "object", "properties": properties, "required": required}


def _resolve_hints(handler: Callable[..., Any]) -> Dict[str, Any]:
    try:
        return dict(get_type_hints(handler))
    except Exception:  # noqa: BLE001 - unresolvable forward refs fall back to raw
        return {}


def _json_type(annotation: Any) -> str:
    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        dict: "object",
        list: "array",
    }
    origin = getattr(annotation, "__origin__", None)
    if origin in (list, List):
        return "array"
    if origin in (dict, Dict):
        return "object"
    if isinstance(annotation, str):
        # ``from __future__ import annotations`` left us a bare name.
        return _STRING_ANNOTATIONS.get(annotation.split("[")[0].strip(), "string")
    return mapping.get(annotation, "string")


_STRING_ANNOTATIONS = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "dict": "object",
    "Dict": "object",
    "list": "array",
    "List": "array",
    "Any": "string",
}


def _ms(started: float) -> float:
    import time

    return (time.perf_counter() - started) * 1000
