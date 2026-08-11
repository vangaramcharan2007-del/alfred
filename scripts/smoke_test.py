#!/usr/bin/env python3
"""Jarvis X Dependency & Import Smoke Test.

Verifies that all declared runtime dependencies are importable and
that the jarvisx production entry point loads without error.

Usage:
    python scripts/smoke_test.py

Requires NO external test framework (no pytest).
Exit code 0 = all checks pass, 1 = at least one failure.
"""

import sys
import importlib

# ---------------------------------------------------------------------------
# Declared runtime dependencies from pyproject.toml -> Python import names
# ---------------------------------------------------------------------------
RUNTIME_DEPS = [
    ("aiofiles",        "aiofiles"),
    ("aiohttp",         "aiohttp"),
    ("cryptography",    "cryptography"),
    ("fastapi",         "fastapi"),
    ("httpx",           "httpx"),
    ("numpy",           "numpy"),
    ("pandas",          "pandas"),
    ("pydantic",        "pydantic"),
    ("PyYAML",          "yaml"),
    ("requests",        "requests"),
    ("websockets",      "websockets"),
    ("psutil",          "psutil"),
]

# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def main() -> int:
    passed = 0
    failed = 0
    errors = []

    print("=" * 60)
    print("  Jarvis X - Dependency & Import Smoke Test")
    print("=" * 60)
    print(f"  Python {sys.version}")
    print()

    # 1. Check each runtime dependency
    print("[1/2] Checking declared runtime dependencies...")
    for pkg_name, import_name in RUNTIME_DEPS:
        try:
            mod = importlib.import_module(import_name)
            ver = getattr(mod, "__version__", "ok")
            print(f"  [PASS] {pkg_name:<20s} ({import_name} -> {ver})")
            passed += 1
        except ImportError as exc:
            print(f"  [FAIL] {pkg_name:<20s} ({import_name}) -> {exc}")
            errors.append(pkg_name)
            failed += 1

    # 2. Check jarvisx production entry point
    print()
    print("[2/2] Checking jarvisx production entry point...")
    try:
        import jarvisx  # noqa: F811
        ver = getattr(jarvisx, "__version__", "unknown")
        print(f"  [PASS] jarvisx package imported (v{ver})")
        passed += 1
    except Exception as exc:
        print(f"  [FAIL] jarvisx import failed -> {exc}")
        errors.append("jarvisx")
        failed += 1

    # Summary
    print()
    print("=" * 60)
    print(f"  PASSED: {passed}   FAILED: {failed}")
    if errors:
        print(f"  Missing / broken: {', '.join(errors)}")
        print()
        print("  Fix: pip install -e .")
    else:
        print("  All dependencies satisfied. Jarvis X is installable.")
    print("=" * 60)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
