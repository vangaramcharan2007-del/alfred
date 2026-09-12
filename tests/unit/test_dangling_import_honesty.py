"""Tests for two dangling imports that were failing dishonestly.

Both reference modules that were never written. The interesting defect was not
the missing module -- that is a product decision -- but what the code did about
it: one fabricated a plausible result, the other dumped a raw traceback and then
reported success to the shell.
"""

import subprocess
import sys
from pathlib import Path

import pytest


def test_read_screen_text_does_not_fabricate_a_result():
    """It used to return the literal "Active Desktop Window" when OCR failed.

    A caller cannot tell fabricated text from text actually read off the screen,
    and the failure was logged at debug level so it never surfaced.
    """
    from jarvisx.organism import Eyes

    result = Eyes().read_screen_text()

    assert result == "", f"fabricated a result instead of reporting none: {result!r}"
    assert result != "Active Desktop Window"


@pytest.mark.parametrize("alias", ["waveform", "overlay", "desktop", "app", "widget"])
def test_waveform_aliases_report_the_missing_module(capfd, alias):
    """All five aliases reached the same unguarded import and raised.

    Asserted as a *return* value, not a raise: the branch this reaches ends in
    `return 1`, and it only becomes a process exit status because of the
    `sys.exit(main())` below. Asserting SystemExit here would have encoded the
    wrong mechanism and passed for the wrong reason.
    """
    from jarvisx import main as main_module

    sys.argv = ["jarvisx.main", alias]
    code = main_module.main()

    assert code == 1, f"{alias!r}: a missing dependency must not report success"
    out = capfd.readouterr().out
    assert "not available" in out
    assert "glowing_waveform_overlay" in out


def test_missing_dependency_reaches_the_process_exit_status():
    """`if __name__ == "__main__": main()` discarded main()'s return value, so
    every `return 1` path in this entry point was swallowed and the process
    always exited 0. Anything scripting it could not detect a failure."""
    repo = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [sys.executable, "-m", "jarvisx.main", "waveform"],
        capture_output=True,
        text=True,
        cwd=str(repo),
        env={"PYTHONPATH": str(repo / "src"), "PATH": "/usr/bin:/bin"},
        timeout=120,
    )

    assert proc.returncode == 1, (
        f"expected a non-zero exit for an unavailable feature, got "
        f"{proc.returncode}\nstdout: {proc.stdout[:400]}\nstderr: {proc.stderr[:400]}"
    )
    assert "not available" in proc.stdout
