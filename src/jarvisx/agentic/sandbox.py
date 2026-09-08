"""Real sandboxed execution for agent-produced code.

The previous ``jarvisx.orchestration.sandbox_harness`` graded code with
``random.random()``.  This module actually runs the code in a jailed
subprocess with timeouts, rlimits, an environment scrub and a workspace
jail, and reports real stdout/stderr/exit codes.  That is what makes the
verification gate meaningful rather than decorative.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger("jarvisx.agentic.sandbox")

# Environment variables that must never leak into sandboxed subprocesses.
_SECRET_PATTERNS = (
    "API_KEY",
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "CREDENTIAL",
    "AUTH",
    "AWS_",
    "AZURE_",
    "GCP_",
    "PRIVATE_KEY",
)

_SAFE_ENV_ALLOWLIST = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONHASHSEED")


@dataclass
class SandboxResult:
    """Structured outcome of a sandboxed execution."""

    ok: bool
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0.0
    timed_out: bool = False
    command: List[str] = field(default_factory=list)
    workdir: str = ""

    def summary(self, max_chars: int = 1500) -> str:
        """Compact human/model-readable digest."""
        parts = [f"exit_code={self.exit_code}", f"duration_ms={self.duration_ms:.0f}"]
        if self.timed_out:
            parts.append("TIMED_OUT")
        if self.stdout.strip():
            parts.append(f"stdout:\n{self.stdout.strip()[:max_chars]}")
        if self.stderr.strip():
            parts.append(f"stderr:\n{self.stderr.strip()[:max_chars]}")
        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "timed_out": self.timed_out,
            "command": self.command,
            "workdir": self.workdir,
        }


def scrub_env(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Build a subprocess environment with secrets removed."""
    env: Dict[str, str] = {}
    for key, value in os.environ.items():
        upper = key.upper()
        if any(pattern in upper for pattern in _SECRET_PATTERNS):
            continue
        env[key] = value
    for key in _SAFE_ENV_ALLOWLIST:
        if key in os.environ:
            env.setdefault(key, os.environ[key])
    if extra:
        env.update(extra)
    return env


def _apply_limits(max_memory_mb: int, max_cpu_seconds: int):
    """Return a preexec_fn that imposes rlimits on the child (POSIX only)."""

    def _limits() -> None:  # pragma: no cover - runs in child process
        try:
            import resource

            resource.setrlimit(resource.RLIMIT_AS, (max_memory_mb * 1024 * 1024,) * 2)
            resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_seconds,) * 2)
            resource.setrlimit(resource.RLIMIT_FSIZE, (64 * 1024 * 1024,) * 2)
            resource.setrlimit(resource.RLIMIT_NPROC, (256,) * 2)
        except (ImportError, ValueError, OSError):
            # Not all platforms expose every limit; degrade rather than fail.
            pass

    return _limits


class SandboxedRunner:
    """Executes untrusted, agent-generated code with hard isolation bounds."""

    def __init__(
        self,
        workspace: Optional[os.PathLike[str] | str] = None,
        timeout_seconds: float = 20.0,
        max_memory_mb: int = 1024,
        max_cpu_seconds: int = 20,
        python_executable: Optional[str] = None,
        allow_network: bool = False,
    ):
        self._owned_workspace = workspace is None
        self.workspace = Path(workspace) if workspace else Path(tempfile.mkdtemp(prefix="alfred_sbx_"))
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self.max_cpu_seconds = max_cpu_seconds
        self.python = python_executable or sys.executable
        self.allow_network = allow_network

    # -- path jailing ------------------------------------------------------ #

    def resolve(self, relative_path: str) -> Path:
        """Resolve a model-supplied path inside the workspace jail.

        Raises :class:`PathEscape` when the path would leave the jail.
        """
        candidate = Path(relative_path)
        if candidate.is_absolute():
            target = candidate.resolve()
        else:
            target = (self.workspace / candidate).resolve()
        root = self.workspace.resolve()
        if target != root and root not in target.parents:
            raise PathEscape(f"'{relative_path}' escapes sandbox root {root}")
        return target

    # -- execution --------------------------------------------------------- #

    def run_python(self, code: str, filename: str = "_agent_snippet.py") -> SandboxResult:
        """Write `code` into the jail and execute it as a subprocess."""
        script = self.workspace / filename
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(code, encoding="utf-8")
        return self.run_command([self.python, "-I", str(script.name)], cwd=self.workspace)

    def run_command(
        self,
        command: Sequence[str],
        cwd: Optional[os.PathLike[str] | str] = None,
        timeout: Optional[float] = None,
        env_extra: Optional[Dict[str, str]] = None,
    ) -> SandboxResult:
        """Run an arbitrary command inside the sandbox jail."""
        workdir = Path(cwd) if cwd else self.workspace
        if not workdir.is_absolute():
            workdir = self.workspace / workdir
        workdir = workdir.resolve()

        root = self.workspace.resolve()
        if workdir != root and root not in workdir.parents:
            raise PathEscape(f"cwd '{workdir}' escapes sandbox root {root}")

        env = scrub_env(env_extra)
        # Never trust the workspace's __pycache__: an agent that rewrites a
        # file with an identical byte size within the same mtime tick would
        # otherwise execute the previous version's bytecode.
        env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
        if not self.allow_network:
            # Not a security boundary on its own, but it stops accidental egress
            # for tools that honour the standard proxy variables.
            env["no_proxy"] = ""
            env["HTTP_PROXY"] = "http://127.0.0.1:9"
            env["HTTPS_PROXY"] = "http://127.0.0.1:9"

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                list(command),
                cwd=str(workdir),
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout_seconds,
                env=env,
                preexec_fn=_apply_limits(self.max_memory_mb, self.max_cpu_seconds)
                if os.name == "posix"
                else None,
            )
            duration = (time.perf_counter() - started) * 1000
            return SandboxResult(
                ok=completed.returncode == 0,
                exit_code=completed.returncode,
                stdout=completed.stdout or "",
                stderr=completed.stderr or "",
                duration_ms=duration,
                command=list(command),
                workdir=str(workdir),
            )
        except subprocess.TimeoutExpired as exc:
            duration = (time.perf_counter() - started) * 1000
            return SandboxResult(
                ok=False,
                exit_code=-1,
                stdout=_decode(exc.stdout),
                stderr=_decode(exc.stderr) or f"timed out after {timeout or self.timeout_seconds}s",
                duration_ms=duration,
                timed_out=True,
                command=list(command),
                workdir=str(workdir),
            )
        except FileNotFoundError as exc:
            duration = (time.perf_counter() - started) * 1000
            return SandboxResult(
                ok=False,
                exit_code=127,
                stderr=f"command not found: {exc}",
                duration_ms=duration,
                command=list(command),
                workdir=str(workdir),
            )

    def run_pytest(self, path: str = ".", args: Optional[Sequence[str]] = None) -> SandboxResult:
        """Execute the sandbox's test suite and return the real result."""
        command = [self.python, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", path]
        command.extend(args or [])
        return self.run_command(command, cwd=self.workspace)

    # -- lifecycle --------------------------------------------------------- #

    def write_file(self, relative_path: str, content: str) -> str:
        """Write a file inside the jail; returns the absolute path written."""
        target = self.resolve(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return str(target)

    def read_file(self, relative_path: str) -> str:
        return self.resolve(relative_path).read_text(encoding="utf-8")

    def list_files(self) -> List[str]:
        root = self.workspace.resolve()
        return sorted(
            str(p.relative_to(root))
            for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        )

    def cleanup(self) -> None:
        if self._owned_workspace and self.workspace.exists():
            shutil.rmtree(self.workspace, ignore_errors=True)

    def __enter__(self) -> "SandboxedRunner":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.cleanup()


class PathEscape(ValueError):
    """Raised when a model-supplied path would leave the sandbox jail."""


def _decode(raw: Any) -> str:
    if raw is None:
        return ""
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="replace")
    return str(raw)
