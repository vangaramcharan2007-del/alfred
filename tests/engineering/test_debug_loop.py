from __future__ import annotations

import sys
from pathlib import Path
from jarvisx.engineering.debug_loop import DebugLoopEngine


def test_real_debug_loop_execution(tmp_path: Path) -> None:
    # 1. Setup a repository with a clean test suite first
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    clean_test = tests_dir / "test_simple.py"
    clean_test.write_text("def test_ok():\n    assert 1 + 1 == 2\n", encoding="utf-8")

    engine = DebugLoopEngine(tmp_path)
    res_clean = engine.debug_repository(test_cmd=[sys.executable, "-m", "pytest", str(tests_dir), "-q"])
    assert res_clean.success is True
    assert len(res_clean.attempts) == 1
    assert res_clean.attempts[0].return_code == 0
    assert "REAL DEBUGGING LOOP REPORT" in res_clean.generate_report()

    # 2. Setup a simulated failing script with syntax error
    bad_py = tmp_path / "broken_script.py"
    bad_py.write_text("def faulty():\n    return =\n", encoding="utf-8")

    res_faulty = engine.debug_repository(test_cmd=[sys.executable, "-m", "py_compile", str(bad_py)])
    # Verify attempt logging and syntax analysis
    assert len(res_faulty.attempts) >= 1
    assert any(att.return_code != 0 for att in res_faulty.attempts)
    assert any("SyntaxError" in att.compiler_output or "SyntaxError" in att.traceback_snippet for att in res_faulty.attempts)
    assert len(res_faulty.attempts) <= DebugLoopEngine.MAX_RETRIES
