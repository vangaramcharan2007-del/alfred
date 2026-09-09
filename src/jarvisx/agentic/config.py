"""Preferences, so nobody has to type 17 flags every session.

The whole point of this agent is to remove manual work, and retyping
``--persona jarvis --physical --energy low`` on every launch is manual work.
So preferences live in one small JSON file that is found automatically.

Search order, first match wins:

    --config <path>            explicit
    ./alfred.json              project-local, checked into the repo
    ./var/agentic/config.json  project-local, gitignored scratch
    ~/.alfred.json             machine-wide

Everything is optional. With no file at all, every default still applies, and a
CLI flag always beats the file.

Two rules this module holds to:

- **A broken config must never stop the agent starting.** A typo in JSON should
  cost you your preference, not your assistant. Malformed files are reported and
  ignored.
- **No magic.** :func:`load` always says which file it used, so a user who
  wonders why their persona is not taking effect can find out in one line.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("jarvisx.agentic.config")

# Preference keys the runtime understands. Anything else in the file is ignored
# rather than fatal, so a stale key from an older version cannot break startup.
KNOWN_KEYS = frozenset(
    {
        "persona",
        "energy",
        "physical",
        "physical_dry_run",
        "watch",
        "quiet",
        "wake_word",
        "interval",
        "switch_window",
        "switch_threshold",
        "grace",
        "break_after",
        "turns",
        "state",
        "auto_capture",
    }
)

# Values that must be one of a fixed set. Checked here so a typo produces a
# clear message at load time instead of a confusing failure much later.
_ENUM_KEYS = {
    "persona": ("plain", "stark", "friday", "jarvis", "eevee"),
    "energy": ("low", "medium", "high"),
}


@dataclass
class LoadedConfig:
    """The resolved preferences, plus where they came from."""

    values: Dict[str, Any] = field(default_factory=dict)
    source: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return self.source is not None

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def describe(self) -> str:
        """One honest line about where preferences came from."""
        if not self.found:
            return "no config file (using defaults)"
        keys = ", ".join(f"{k}={v!r}" for k, v in sorted(self.values.items()))
        return f"{self.source} ({keys or 'empty'})"


def candidate_paths(explicit: Optional[str] = None) -> List[Path]:
    """Every location that could hold a config file, in priority order."""
    paths: List[Path] = []
    if explicit:
        paths.append(Path(explicit).expanduser())
    paths.append(Path("alfred.json"))
    paths.append(Path("var/agentic/config.json"))
    home = os.path.expanduser("~")
    paths.append(Path(home) / ".alfred.json")
    return paths


def load(explicit: Optional[str] = None) -> LoadedConfig:
    """Find and read the first config file that exists.

    Never raises. A missing, unreadable or malformed file yields defaults plus
    a warning, because losing a preference is acceptable and losing the agent
    is not.
    """
    result = LoadedConfig()

    for path in candidate_paths(explicit):
        if not path.exists():
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            result.warnings.append(f"{path}: unreadable ({exc}); using defaults")
            logger.warning("config %s unreadable: %s", path, exc)
            # An explicitly named file that cannot be read is worth surfacing,
            # but still must not be fatal.
            continue

        if not isinstance(raw, dict):
            result.warnings.append(f"{path}: expected a JSON object, got {type(raw).__name__}")
            continue

        values, problems = _validate(raw)
        result.values = values
        result.warnings.extend(f"{path}: {p}" for p in problems)
        result.source = path
        return result

    return result


def _validate(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Keep the keys we understand; report the rest instead of failing."""
    values: Dict[str, Any] = {}
    problems: List[str] = []

    for key, value in raw.items():
        if key not in KNOWN_KEYS:
            problems.append(f"ignoring unknown key {key!r}")
            continue
        allowed = _ENUM_KEYS.get(key)
        if allowed is not None and value not in allowed:
            problems.append(
                f"{key}={value!r} is not one of {', '.join(allowed)}; ignoring"
            )
            continue
        values[key] = value

    return values, problems


def merge(config: LoadedConfig, overrides: Dict[str, Any]) -> Dict[str, Any]:
    """File values, then CLI values on top.

    Only keys the caller actually set are treated as overrides. Argparse
    defaults are indistinguishable from an explicit choice once parsed, so the
    caller passes only what the user really gave.
    """
    merged = dict(config.values)
    for key, value in overrides.items():
        if value is not None:
            merged[key] = value
    return merged


def default_path() -> Path:
    """Where `--save-config` writes: project-local and gitignored."""
    return Path("var/agentic/config.json")


def save(values: Dict[str, Any], path: Optional[Path | str] = None) -> Path:
    """Write preferences so the next launch needs no flags."""
    target = Path(path) if path else default_path()
    clean = {k: v for k, v in values.items() if k in KNOWN_KEYS and v is not None}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(clean, indent=2) + "\n", encoding="utf-8")
    return target
