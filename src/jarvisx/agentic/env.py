"""Environment and credential discovery for the agentic layer.

Nothing in this repository loads ``.env`` into ``os.environ``. ``python-dotenv``
is not a dependency, and ``GroqLLMProvider`` works around that with its own
ad-hoc reader (including a hardcoded ``E:/project-jarvis-x/.env`` path). The
consequence is that a key sitting in ``.env`` never reaches code that reads
``os.getenv(...)`` — which silently downgrades every agent to offline mode.

:func:`load_dotenv` fixes that once, for the whole layer, with no third-party
dependency. Keys already present in the real environment always win, so an
exported variable is never overwritten by a stale file.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

logger = logging.getLogger("jarvisx.agentic.env")

_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Anything matching this is never written to a log line.
_SECRET_KEY_PARTS = ("KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIAL")

# Redact common provider key shapes in any message we emit.
_REDACT_PATTERNS = (
    re.compile(r"gsk_[0-9A-Za-z\-_]{16,}"),          # Groq
    re.compile(r"sk-or-v1-[0-9A-Za-z\-_]{16,}"),     # OpenRouter
    re.compile(r"sk-[0-9A-Za-z\-_]{16,}"),           # OpenAI
    re.compile(r"AIza[0-9A-Za-z\-_\-]{16,}"),        # Google
)

_loaded_from: List[Path] = []


def candidate_env_files(start: Optional[os.PathLike[str] | str] = None) -> List[Path]:
    """Every ``.env`` worth reading, most specific first."""
    roots: List[Path] = []
    if start:
        roots.append(Path(start))
    roots.append(Path.cwd())

    # Walk up from the cwd to the repository root (or the filesystem root).
    here = Path(__file__).resolve()
    for parent in here.parents:
        roots.append(parent)
        if (parent / ".git").exists():
            break

    found: List[Path] = []
    seen: set[str] = set()
    for root in roots:
        if not root:
            continue
        base = root if root.is_dir() else root.parent
        for name in (".env", ".env.local"):
            candidate = (base / name).resolve()
            key = str(candidate)
            if key in seen:
                continue
            seen.add(key)
            if candidate.is_file():
                found.append(candidate)
    return found


def parse_env(text: str) -> Dict[str, str]:
    """Parse ``.env`` contents. Handles quotes, ``export``, comments, blanks."""
    values: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not _KEY_RE.match(key):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values


def load_dotenv(
    start: Optional[os.PathLike[str] | str] = None,
    override: bool = False,
) -> List[Path]:
    """Load ``.env`` files into ``os.environ``. Idempotent.

    Returns the list of files actually read. Existing environment variables win
    unless ``override`` is true.
    """
    loaded: List[Path] = []
    # Least specific first, so a nearer file wins over a parent-directory one.
    for path in reversed(candidate_env_files(start)):
        try:
            parsed = parse_env(path.read_text(encoding="utf-8"))
        except OSError as exc:
            logger.debug("could not read %s: %s", path, exc)
            continue
        applied = 0
        for key, value in parsed.items():
            if override or key not in os.environ:
                os.environ[key] = value
                applied += 1
        if applied:
            loaded.append(path)
            logger.info("loaded %d var(s) from %s", applied, path)
    _loaded_from.extend(p for p in loaded if p not in _loaded_from)
    return loaded


def loaded_files() -> List[Path]:
    return list(_loaded_from)


def redact(text: str) -> str:
    """Strip anything that looks like a provider key from a message."""
    out = text or ""
    for pattern in _REDACT_PATTERNS:
        out = pattern.sub("[REDACTED_KEY]", out)
    return out


def get_secret(name: str, start: Optional[os.PathLike[str] | str] = None) -> Optional[str]:
    """Read a credential from the environment or ``.env``, without logging it."""
    value = os.environ.get(name)
    if value:
        return value.strip()
    for path in candidate_env_files(start):
        try:
            parsed = parse_env(path.read_text(encoding="utf-8"))
        except OSError:
            continue
        if parsed.get(name):
            return parsed[name].strip()
    return None


def describe_credentials(start: Optional[os.PathLike[str] | str] = None) -> Dict[str, object]:
    """Safe, redacted summary of which providers are configured.

    Reports only whether a key exists and a fingerprint of it — never the key.
    """
    load_dotenv(start)
    names = (
        "GROQ_API_KEY",
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OMNIROUTE_API_KEY",
    )
    found: Dict[str, str] = {}
    for name in names:
        value = get_secret(name, start)
        if value:
            found[name] = fingerprint(value)
    return {
        "configured": sorted(found),
        "fingerprints": found,
        "env_files": [str(p) for p in candidate_env_files(start)],
    }


def fingerprint(secret: str) -> str:
    """A non-reversible hint so the user can tell two keys apart."""
    if not secret:
        return "(empty)"
    import hashlib

    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()[:8]
    return f"{secret[:4]}…{digest}"


def is_secret_name(name: str) -> bool:
    upper = name.upper()
    return any(part in upper for part in _SECRET_KEY_PARTS)


def required_model_env() -> Dict[str, Optional[str]]:
    """The settings that decide which backend ``AutoBackend`` will pick."""
    load_dotenv()
    return {
        "ALFRED_AGENT_BACKEND": os.environ.get("ALFRED_AGENT_BACKEND"),
        "ALFRED_AGENT_MODEL": os.environ.get("ALFRED_AGENT_MODEL"),
        "GROQ_API_KEY": "***" if get_secret("GROQ_API_KEY") else None,
        "GROQ_MODEL": os.environ.get("GROQ_MODEL") or os.environ.get("CODER_MODEL"),
        "OPENROUTER_API_KEY": "***" if get_secret("OPENROUTER_API_KEY") else None,
        "OLLAMA_BASE_URL": os.environ.get("OLLAMA_BASE_URL"),
    }
