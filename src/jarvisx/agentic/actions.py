"""Physical reach for the harness: the hands that touch the real machine.

The repo already had real physical actions in ``voice/eevee_groq.py`` — opening
apps, running PowerShell, reading and writing files. But that class shells out
to ``powershell -Command`` with no policy gate, no confirmation, no trace and
no budget. A model that decides to run ``rm -rf ~`` is stopped by nothing but
the model's own judgement.

This module re-exposes those capabilities as ordinary :class:`AgentTool`
entries, which buys them everything the harness already has:

    policy      destructive patterns are refused before execution
    permission  shell execution is CONFIRM, not SAFE
    trace       every invocation is recorded in the run's JSONL
    budget      a runaway loop hits a ceiling instead of your filesystem
    verify      the result is checked, not assumed

Nothing here is sandboxed the way ``SandboxedRunner`` sandboxes generated code —
these tools are *supposed* to reach the real desktop. That is exactly why they
are gated instead.

Every tool raises on failure rather than returning ``{"ok": False}``. A soft
failure dict is invisible to ``Observation.ok``, so the harness would grade a
crashed tool as a success.
"""

from __future__ import annotations

import logging
import os
import platform
import re
import shutil
import subprocess
import urllib.parse
import webbrowser
from typing import Any, Callable, Dict, Optional

from jarvisx.agentic.registry import AgentToolRegistry
from jarvisx.tools.tool_kernel import PermissionLevel

logger = logging.getLogger("jarvisx.agentic.actions")

# --------------------------------------------------------------------------- #
# Policy
# --------------------------------------------------------------------------- #

# Refused outright, regardless of who asked. These are not "dangerous, ask
# first" — there is no version of an ADHD automation assistant that should ever
# run them, and a prompt-injected model will try.
_BLOCKED_RE = re.compile(
    r"""(?:
          rm\s+(?:-[a-z]*[rf][a-z]*\s+)+
        | rd\s+/s | del\s+/[sqf] | rmdir\s+/s
        | format\s+[a-z]:
        | mkfs | dd\s+if=
        | shutdown | reboot | halt | init\s+0
        | diskpart
        | :\(\)\s*\{.*\};\s*:          # fork bomb
        | Remove-Item\s+.*-Recurse\s+.*-Force
        | Clear-Disk | Clear-Content\s+[A-Z]:\\
    )""",
    re.IGNORECASE | re.VERBOSE,
)

# Needs an explicit human yes. Reversible, but annoying or costly to undo.
_CONFIRM_RE = re.compile(
    r"""(?:
          \bsudo\b | \brunas\b | \bgksudo\b
        | \bchmod\s+[0-7]{3,4}\b | \bchown\b
        | \bkill(?:all)?\b | \btaskkill\b
        | \bgit\s+(?:push|reset|clean|checkout\s+--)\b
        | \bnpm\s+(?:publish|uninstall)\b | \bpip\s+uninstall\b
        | \bapt(?:-get)?\s+(?:remove|purge)\b
        | \b>\s*/dev/ | \breg\s+(?:add|delete)\b
        | \bschtasks\b | \bcrontab\b
    )""",
    re.IGNORECASE | re.VERBOSE,
)

# App aliases. Kept short and explicit: guessing an executable name from a
# fuzzy string is how you end up launching the wrong thing.
_APP_ALIASES = {
    "code": "code",
    "vscode": "code",
    "vs code": "code",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "terminal": "x-terminal-emulator",
    "files": "xdg-open",
    "explorer": "explorer",
    "browser": "xdg-open",
    "chrome": "google-chrome",
    "spotify": "spotify",
}

# Sites that are opened directly rather than searched.
_DIRECT_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chat.openai.com",
    "spotify": "https://open.spotify.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
}


def classify_command(command: str) -> str:
    """Return "blocked", "confirm" or "allow" for a shell command.

    Pure and deterministic so it can be tested without executing anything.
    """
    text = (command or "").strip()
    if not text:
        return "blocked"
    if _BLOCKED_RE.search(text):
        return "blocked"
    if _CONFIRM_RE.search(text):
        return "confirm"
    return "allow"


def resolve_target(target: str) -> Dict[str, Any]:
    """Turn "play lofi on youtube" into something launchable.

    Returns ``{"kind": "url"|"app", "value": ..., "label": ...}``. Never raises:
    an unrecognised target becomes a web search, which is the most useful guess.
    """
    raw = (target or "").strip()
    lowered = raw.lower()

    if re.match(r"^https?://", lowered):
        return {"kind": "url", "value": raw, "label": raw}

    # Strip the verb so "open youtube" and "youtube" resolve identically.
    stripped = re.sub(
        r"^(?:please\s+)?(?:open|launch|start|run|play|search|watch|listen\s+to)\s+",
        "",
        lowered,
    ).strip()

    for site, url in _DIRECT_SITES.items():
        # Match the site name anywhere, not just at the front: "play lofi on
        # youtube" still names YouTube, and sending that to a Google search
        # instead of a YouTube search is exactly the kind of small miss that
        # makes an assistant feel broken.
        if not re.search(rf"\b{re.escape(site)}\b", stripped):
            continue
        # Everything that is not the site name is the query.
        query = re.sub(
            r"\b(?:on|in|the|for|please|open|play|search|watch|listen\s+to|"
            + re.escape(site)
            + r")\b",
            " ",
            stripped,
            flags=re.IGNORECASE,
        )
        query = re.sub(r"\s+", " ", query).strip()
        if query and len(query) > 1:
            if site == "youtube":
                url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            elif site == "spotify":
                url = f"https://open.spotify.com/search/{urllib.parse.quote(query)}"
            elif site == "google":
                url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            return {"kind": "url", "value": url, "label": f"{site}: {query}"}
        return {"kind": "url", "value": url, "label": site}

    for alias, executable in _APP_ALIASES.items():
        if stripped == alias or stripped.startswith(f"{alias} "):
            return {"kind": "app", "value": executable, "label": alias}

    # Unknown: searching is more useful than failing.
    return {
        "kind": "url",
        "value": f"https://www.google.com/search?q={urllib.parse.quote(raw)}",
        "label": f"search: {raw}",
    }


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #


def build_action_tools(
    registry: Optional[AgentToolRegistry] = None,
    confirm: Optional[Callable[[str], bool]] = None,
    workspace: Optional[str] = None,
    dry_run: bool = False,
) -> AgentToolRegistry:
    """Register the physical action tools.

    ``confirm`` is called for CONFIRM-level commands and must return True to
    proceed. Defaults to refusing, so an unattended run can never execute
    something that needed a human.

    ``dry_run`` resolves and validates everything but performs no launch. Used
    by tests and by headless machines.
    """
    reg = registry or AgentToolRegistry()
    confirm_fn = confirm or (lambda prompt: False)
    root = os.path.abspath(workspace or os.getcwd())

    def _jail(path: str) -> str:
        """Resolve inside the workspace; refuse anything that escapes it."""
        candidate = os.path.abspath(
            path if os.path.isabs(path) else os.path.join(root, path)
        )
        if candidate != root and not candidate.startswith(root + os.sep):
            raise PermissionError(f"{path!r} is outside the workspace {root}")
        return candidate

    @reg.tool(
        name="open_app_or_website",
        description=(
            "Open a website or launch a desktop app. Accepts a URL, a known "
            "app name (code, notepad, calculator, terminal), or a natural "
            "request like 'play lofi on youtube'."
        ),
        permission=PermissionLevel.SAFE,
        tags=("desktop", "physical"),
        input_schema={
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "URL, app name, or natural request",
                }
            },
            "required": ["target"],
        },
    )
    def open_app_or_website(target: str) -> Dict[str, Any]:
        resolved = resolve_target(target)
        if dry_run:
            return {"ok": True, "dry_run": True, **resolved}

        if resolved["kind"] == "url":
            opened = webbrowser.open(resolved["value"])
            if not opened:
                raise RuntimeError(
                    f"no browser could open {resolved['value']!r}"
                )
            return {"ok": True, **resolved}

        executable = shutil.which(resolved["value"])
        if not executable:
            raise RuntimeError(
                f"{resolved['value']!r} is not installed or not on PATH"
            )
        subprocess.Popen(  # noqa: S603 - resolved from a fixed alias table
            [executable],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {"ok": True, **resolved}

    @reg.tool(
        name="run_system_command",
        description=(
            "Run a shell command on the user's machine. Destructive commands "
            "are refused; privileged or hard-to-undo commands require "
            "confirmation."
        ),
        permission=PermissionLevel.CONFIRM,
        tags=("shell", "physical"),
        input_schema={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command"}
            },
            "required": ["command"],
        },
    )
    def run_system_command(command: str) -> Dict[str, Any]:
        verdict = classify_command(command)
        if verdict == "blocked":
            raise PermissionError(
                f"refused to run {command!r}: it matches a destructive pattern"
            )
        if verdict == "confirm" and not confirm_fn(command):
            raise PermissionError(
                f"{command!r} needs your confirmation and did not get it"
            )
        if dry_run:
            return {"ok": True, "dry_run": True, "verdict": verdict, "command": command}

        if platform.system() == "Windows":
            argv = ["powershell", "-NoProfile", "-Command", command]
        else:
            argv = ["/bin/sh", "-c", command]

        try:
            result = subprocess.run(  # noqa: S603 - gated by classify_command
                argv, capture_output=True, text=True, timeout=30
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"command timed out after 30s: {command!r}") from exc

        output = (result.stdout or "").strip() or (result.stderr or "").strip()
        if result.returncode != 0:
            raise RuntimeError(
                f"command exited {result.returncode}: {output[:300] or 'no output'}"
            )
        return {"ok": True, "verdict": verdict, "output": output[:1000]}

    @reg.tool(
        name="create_file",
        description="Write a file inside the agent workspace.",
        permission=PermissionLevel.SAFE,
        tags=("filesystem",),
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Workspace-relative path"},
                "content": {"type": "string", "description": "File contents"},
            },
            "required": ["path", "content"],
        },
    )
    def create_file(path: str, content: str) -> Dict[str, Any]:
        absolute = _jail(path)
        if dry_run:
            return {"ok": True, "dry_run": True, "path": absolute}
        os.makedirs(os.path.dirname(absolute) or root, exist_ok=True)
        with open(absolute, "w", encoding="utf-8") as handle:
            handle.write(content)
        return {"ok": True, "path": absolute, "bytes": len(content.encode("utf-8"))}

    @reg.tool(
        name="read_file",
        description="Read a file from the agent workspace.",
        permission=PermissionLevel.SAFE,
        tags=("filesystem",),
        input_schema={
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Workspace-relative path"}},
            "required": ["path"],
        },
    )
    def read_file(path: str) -> Dict[str, Any]:
        absolute = _jail(path)
        with open(absolute, "r", encoding="utf-8", errors="replace") as handle:
            content = handle.read()
        return {"ok": True, "path": absolute, "content": content[:8000]}

    @reg.tool(
        name="system_vitals",
        description="Report CPU, memory and battery, if the OS exposes them.",
        permission=PermissionLevel.SAFE,
        tags=("system",),
        input_schema={"type": "object", "properties": {}},
    )
    def system_vitals() -> Dict[str, Any]:
        # psutil is optional. Degrading beats crashing: vitals are the least
        # important thing here and must never take the agent down with them.
        try:
            import psutil  # type: ignore
        except ImportError:
            load = os.getloadavg()[0] if hasattr(os, "getloadavg") else None
            return {
                "ok": True,
                "degraded": True,
                "note": "psutil not installed; reporting what the OS gives us",
                "load_average_1m": load,
                "platform": platform.platform(),
            }
        memory = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        return {
            "ok": True,
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "memory_percent": memory.percent,
            "battery_percent": battery.percent if battery else None,
        }

    return reg
