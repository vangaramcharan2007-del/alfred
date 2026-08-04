from __future__ import annotations

import sys
import time
from pathlib import Path
from jarvisx.engineering.verification import ChangeVerifier


def test_change_verification_and_reporting(tmp_path: Path) -> None:
    verifier = ChangeVerifier(tmp_path)
    snapshot = verifier.capture_snapshot()

    # 1. Test failure when no files are changed
    report_unmod = verifier.verify_changes(
        mission_goal="Empty modification check",
        reason="Test zero change verification",
        snapshot=snapshot,
        test_cmd=[sys.executable, "-c", "import sys; sys.exit(0)"]
    )
    assert report_unmod.success is False
    assert len(report_unmod.files_changed) == 0

    # 2. Test success after modifying a file cleanly
    time.sleep(0.01) # ensure timestamp increment
    new_module = tmp_path / "new_feature.py"
    new_module.write_text("def add(x: int, y: int) -> int:\n    return x + y\n", encoding="utf-8")

    report_mod = verifier.verify_changes(
        mission_goal="Add math helper feature",
        reason="Implemented math functions cleanly",
        snapshot=snapshot,
        test_cmd=[sys.executable, "-c", "import sys; sys.exit(0)"]
    )
    assert report_mod.success is True
    assert "new_feature.py" in report_mod.files_changed
    assert report_mod.build_clean is True
    assert report_mod.tests_passed is True

    output = report_mod.generate_report()
    assert "CHANGE REPORT: SUCCESS" in output
    assert "new_feature.py" in output

    # 3. Test build failure when modified Python file has syntax error
    bad_file = tmp_path / "bad_syntax.py"
    bad_file.write_text("def error(\n", encoding="utf-8")
    report_bad = verifier.verify_changes(
        mission_goal="Broken syntax check",
        reason="Test compilation check",
        explicit_modified_files=["bad_syntax.py"],
        test_cmd=[sys.executable, "-c", "import sys; sys.exit(0)"]
    )
    assert report_bad.success is False
    assert report_bad.build_clean is False
    assert any("Syntax compilation check failed" in ev for ev in report_bad.evidence)
