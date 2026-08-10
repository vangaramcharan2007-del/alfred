from __future__ import annotations
import asyncio
import shlex
from pathlib import Path
from typing import Dict, Any, List, Optional

class SandboxSecurityError(PermissionError):
    """Raised when a command violates sandbox security policies."""
    pass

class SandboxManager:
    _SHELL_CONTROL_TOKENS = {"&&", "||", ";", "|", ">", ">>", "<", "2>", "2>>"}

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

    def parse_command(self, command: str) -> List[str]:
        """Parse one command invocation without granting shell interpretation."""
        tokens = [self._strip_wrapping_quotes(token) for token in shlex.split(command, posix=False)]
        if not tokens:
            raise SandboxSecurityError("Empty command passed to sandbox.")

        if any(token in self._SHELL_CONTROL_TOKENS for token in tokens):
            raise SandboxSecurityError("Shell control operators are not allowed in sandbox commands.")
        
        base_cmd = Path(tokens[0]).name.lower()
        if base_cmd.endswith(".exe") or base_cmd.endswith(".bat") or base_cmd.endswith(".cmd"):
            base_cmd = base_cmd.rsplit(".", 1)[0]

        if base_cmd not in self.allowed_commands:
            raise SandboxSecurityError(f"Command '{base_cmd}' is not allowed in sandbox allowlist: {sorted(self.allowed_commands)}")

        return tokens

    def validate_command(self, command: str) -> str:
        """Legacy validation API returning the normalized executable name."""
        tokens = self.parse_command(command)
        base_cmd = Path(tokens[0]).name.lower()
        if base_cmd.endswith(".exe") or base_cmd.endswith(".bat") or base_cmd.endswith(".cmd"):
            base_cmd = base_cmd.rsplit(".", 1)[0]
        return base_cmd

    @staticmethod
    def _strip_wrapping_quotes(token: str) -> str:
        if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
            return token[1:-1]
        return token

    async def execute_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        tokens = self.parse_command(command)
        timeout_val = timeout or self.default_timeout_seconds

        process = await asyncio.create_subprocess_exec(
            *tokens,
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
