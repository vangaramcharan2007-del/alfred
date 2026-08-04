from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
VENV_PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
MANIFEST_DIR = SRC_DIR / "jarvisx" / "capabilities" / "manifests"

RUNTIME_IMPORTS = {
    "aiohttp": "aiohttp",
    "fastapi": "fastapi",
    "httpx": "httpx",
    "numpy": "numpy",
    "pandas": "pandas",
    "pydantic": "pydantic",
    "requests": "requests",
    "psutil": "psutil",
    "PyYAML": "yaml",
    "pyzmq": "zmq",
    "websockets": "websockets",
}

DEV_IMPORTS = {
    "pytest": "pytest",
    "pytest-asyncio": "pytest_asyncio",
    "pytest-cov": "pytest_cov",
    "pytesseract": "pytesseract",
    "Pillow": "PIL",
    "opencv-python": "cv2",
    "PyAutoGUI": "pyautogui",
    "pygetwindow": "pygetwindow",
    "pywinauto": "pywinauto",
    "mss": "mss",
    "pyperclip": "pyperclip",
}


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    critical: bool = False


def marker(ok: bool) -> str:
    return "OK" if ok else "FAIL"


def has_module(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def run_git_status() -> Check:
    try:
        result = subprocess.run(
            ["git", "-c", "core.fsmonitor=false", "status", "--short", "--branch"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        return Check("git", False, f"git status failed: {exc}")

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return Check("git", False, detail or "git status returned a non-zero exit code.")
    first_line = result.stdout.splitlines()[0] if result.stdout.splitlines() else "status unavailable"
    return Check("git", True, first_line)


def validate_manifests() -> Check:
    required = {"name", "version", "api_version", "description", "category"}
    if not MANIFEST_DIR.exists():
        return Check("capability manifests", False, f"Missing directory: {MANIFEST_DIR}", critical=True)

    failures: list[str] = []
    names: list[str] = []
    for path in sorted(MANIFEST_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"{path.name}: invalid JSON ({exc})")
            continue
        missing = sorted(required - set(data))
        if missing:
            failures.append(f"{path.name}: missing {', '.join(missing)}")
        else:
            names.append(str(data["name"]))

    if failures:
        return Check("capability manifests", False, "; ".join(failures), critical=True)
    return Check("capability manifests", True, ", ".join(names) or "no manifests found")


def collect_checks() -> list[Check]:
    checks: list[Check] = []
    checks.append(
        Check(
            "python version",
            sys.version_info >= (3, 11),
            sys.version.split()[0],
            critical=True,
        )
    )
    checks.append(Check("project root", (ROOT / "pyproject.toml").exists(), str(ROOT), critical=True))
    checks.append(Check("virtual environment", VENV_PYTHON.exists(), str(VENV_PYTHON)))
    checks.append(validate_manifests())
    checks.append(run_git_status())

    for package, module in RUNTIME_IMPORTS.items():
        checks.append(Check(f"runtime import: {package}", has_module(module), module, critical=True))

    for package, module in DEV_IMPORTS.items():
        checks.append(Check(f"dev import: {package}", has_module(module), module))

    return checks


def main() -> int:
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    print("Jarvis X diagnostics")
    print(f"Repository: {ROOT}")
    print()

    checks = collect_checks()
    for check in checks:
        print(f"[{marker(check.ok)}] {check.name}: {check.detail}")

    failed_critical = [check for check in checks if check.critical and not check.ok]
    if failed_critical:
        print()
        print("Critical checks failed. Run .\\install.ps1, then rerun diagnostics.")
        return 1

    print()
    print("Diagnostics complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
