from __future__ import annotations

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"
VENV_PYTHON = VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PROJECT_DIRS = (
    "var/log",
    "data",
    "backups",
    "logs",
    "scratch",
    "vault",
    "workspace",
)


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(command))
    return subprocess.run(command, cwd=ROOT, text=True, check=check)


def ensure_python_version() -> None:
    if sys.version_info < (3, 11):
        raise SystemExit("Jarvis X requires Python 3.11 or newer.")


def ensure_venv(recreate: bool = False) -> None:
    if recreate and VENV_DIR.exists():
        raise SystemExit("Refusing to delete .venv automatically. Remove it manually, then rerun bootstrap.")

    if VENV_PYTHON.exists():
        print(f"Using existing virtual environment: {VENV_DIR}")
        return

    print(f"Creating virtual environment: {VENV_DIR}")
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(VENV_DIR)


def install_project(extras: str) -> None:
    spec = f".[{extras}]" if extras else "."
    run([str(VENV_PYTHON), "-m", "pip", "install", "-e", spec])


def ensure_directories() -> None:
    for relative in PROJECT_DIRS:
        path = ROOT / relative
        path.mkdir(parents=True, exist_ok=True)
        print(f"Ensured directory: {path.relative_to(ROOT)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap the Jarvis X project environment.")
    parser.add_argument(
        "--extras",
        default="dev",
        help="Comma-separated pyproject extras to install. Defaults to dev.",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Create the venv and directories without installing Python dependencies.",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Reserved safety flag. Does not delete .venv automatically.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_python_version()

    if not (ROOT / "pyproject.toml").exists():
        raise SystemExit("pyproject.toml not found. Run bootstrap from the project repository.")

    ensure_venv(recreate=args.recreate)
    ensure_directories()

    if args.skip_install or os.environ.get("JARVISX_BOOTSTRAP_SKIP_INSTALL") == "1":
        print("Skipped dependency installation.")
        return 0

    try:
        install_project(args.extras.strip())
    except subprocess.CalledProcessError as exc:
        print("\nDependency installation failed.")
        print("If you are offline, rerun when package wheels are available or use --skip-install for directory setup only.")
        return exc.returncode or 1

    print("\nBootstrap complete.")
    print(f"Python: {VENV_PYTHON}")
    print("Run tests with: .\\test.ps1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
