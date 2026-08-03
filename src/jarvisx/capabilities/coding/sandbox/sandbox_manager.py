from __future__ import annotations
import asyncio
import shlex
from pathlib import Path
from typing import Dict, Any, List, Optional

class SandboxSecurityError(PermissionError):
    """Raised when a command violates sandbox security policies."""
    pass

class SandboxManager:
    def __init__(
        self,
        allowed_commands: Optional[List[str]] = None,
        default_timeout_seconds: float = 30.0,
        max_output_length: int = 50_000
    ):
        self.allowed_commands = set(
            allowed_commands or ["python", "pytest", "npm", "git", "echo", "ls", "dir", "cat", "node"]
        )
        self.default_timeout_seconds = default_timeout_seconds
        self.max_output_length = max_output_length

    def validate_command(self, command: str) -> str:
        tokens = shlex.split(command, posix=False)
        if not tokens:
            raise SandboxSecurityError("Empty command passed to sandbox.")
        
        base_cmd = Path(tokens[0]).name.lower()
        if base_cmd.endswith(".exe") or base_cmd.endswith(".bat") or base_cmd.endswith(".cmd"):
            base_cmd = base_cmd.rsplit(".", 1)[0]

        if base_cmd not in self.allowed_commands:
            raise SandboxSecurityError(f"Command '{base_cmd}' is not allowed in sandbox allowlist: {sorted(self.allowed_commands)}")
        
        return base_cmd

    async def execute_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        self.validate_command(command)
        timeout_val = timeout or self.default_timeout_seconds

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )

        try:
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(), timeout=timeout_val
            )
            stdout_str = stdout_data.decode("utf-8", errors="replace")[:self.max_output_length]
            stderr_str = stderr_data.decode("utf-8", errors="replace")[:self.max_output_length]

            return {
                "exit_code": process.returncode,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "timed_out": False,
                "command": command
            }
        except asyncio.TimeoutError:
            try:
                process.kill()
                await process.wait()
            except Exception:
                pass
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_val} seconds.",
                "timed_out": True,
                "command": command
            }
