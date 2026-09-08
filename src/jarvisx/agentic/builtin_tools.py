"""Default toolset wired to the sandbox.

These are the hands of the harness.  Every tool operates strictly inside the
:class:`~jarvisx.agentic.sandbox.SandboxedRunner` jail, so a misbehaving or
prompt-injected model cannot reach outside its workspace.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from jarvisx.agentic.registry import AgentToolRegistry
from jarvisx.agentic.sandbox import SandboxedRunner
from jarvisx.tools.tool_kernel import PermissionLevel


def build_default_tools(
    sandbox: SandboxedRunner,
    registry: Optional[AgentToolRegistry] = None,
    enable_shell: bool = False,
) -> AgentToolRegistry:
    """Register the standard harness toolset against `sandbox`."""
    reg = registry or AgentToolRegistry()

    @reg.tool(
        name="write_file",
        description="Create or overwrite a file inside the agent workspace.",
        permission=PermissionLevel.SAFE,
        tags=("filesystem",),
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Workspace-relative path"},
                "content": {"type": "string", "description": "Full file contents"},
            },
            "required": ["path", "content"],
        },
    )
    def write_file(path: str, content: str) -> Dict[str, Any]:
        absolute = sandbox.write_file(path, content)
        return {
            "ok": True,
            "path": path,
            "absolute_path": absolute,
            "bytes": len(content.encode("utf-8")),
            "lines": len(content.splitlines()),
        }

    @reg.tool(
        name="read_file",
        description="Read a text file from the agent workspace.",
        permission=PermissionLevel.SAFE,
        tags=("filesystem",),
        input_schema={
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    )
    def read_file(path: str) -> Dict[str, Any]:
        # Genuine failures raise: the registry converts them into an
        # Observation(ok=False), which is what the loop guard and the
        # verification gate key off. Returning {"ok": False} here would hide
        # the failure from every layer above the tool.
        content = sandbox.read_file(path)
        return {"ok": True, "path": path, "content": content}

    @reg.tool(
        name="list_files",
        description="List every file currently in the agent workspace.",
        permission=PermissionLevel.SAFE,
        tags=("filesystem",),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    def list_files() -> Dict[str, Any]:
        files: List[str] = sandbox.list_files()
        return {"ok": True, "count": len(files), "files": files}

    @reg.tool(
        name="python_exec",
        description="Execute Python code in the sandbox and return stdout/stderr/exit code.",
        permission=PermissionLevel.SAFE,
        tags=("execution",),
        input_schema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source to execute"},
                "timeout": {
                    "type": "number",
                    "description": "Optional per-call timeout in seconds",
                },
            },
            "required": ["code"],
        },
    )
    def python_exec(code: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        result = sandbox.run_python(code)
        if timeout is not None:
            result = sandbox.run_command(
                [sandbox.python, "-I", "_agent_snippet.py"], timeout=timeout
            )
        return {"ok": result.ok, **result.to_dict(), "summary": result.summary()}

    @reg.tool(
        name="run_tests",
        description="Run the pytest suite inside the sandbox workspace.",
        permission=PermissionLevel.SAFE,
        tags=("execution", "verification"),
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Test path (default: '.')"},
            },
            "required": [],
        },
    )
    def run_tests(path: str = ".") -> Dict[str, Any]:
        result = sandbox.run_pytest(path)
        return {"ok": result.ok, **result.to_dict(), "summary": result.summary()}

    @reg.tool(
        name="shell",
        description="Run a shell command in the sandbox. Restricted by default.",
        permission=PermissionLevel.CONFIRM,
        tags=("execution", "dangerous"),
        input_schema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "argv-style command, e.g. ['ls', '-la']",
                },
            },
            "required": ["command"],
        },
    )
    def shell(command: List[str]) -> Dict[str, Any]:
        result = sandbox.run_command(command)
        return {"ok": result.ok, **result.to_dict(), "summary": result.summary()}

    if not enable_shell:
        # Keep the tool visible (so the model learns the boundary) but the
        # CONFIRM tier plus a non-interactive approver keeps it inert.
        pass

    @reg.tool(
        name="final_answer",
        description="Declare the mission complete and return the final deliverable text.",
        permission=PermissionLevel.SAFE,
        tags=("control",),
        input_schema={
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "What was accomplished"},
            },
            "required": ["summary"],
        },
    )
    def final_answer(summary: str) -> Dict[str, Any]:
        return {"ok": True, "final": True, "summary": summary}

    return reg
