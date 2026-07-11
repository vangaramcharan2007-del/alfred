from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.core.failures import FailureReport
from jarvisx.runtime import create_default_runtime


class HealthAndFailureTests(unittest.TestCase):
    def test_default_runtime_health_checks_pass(self) -> None:
        runtime = create_default_runtime()
        results = runtime.health.run_all()
        self.assertIn("hermes", results)
        self.assertTrue(all(status.healthy for status in results.values()))

    def test_failure_report_answers_required_questions(self) -> None:
        report = FailureReport.from_exception(
            RuntimeError("boom"),
            agent_id="debug",
            tool_name="file",
            trace_id="trace-1",
        ).to_dict()
        self.assertEqual(report["what_failed"], "RuntimeError")
        self.assertEqual(report["why"], "boom")
        self.assertEqual(report["agent_id"], "debug")
        self.assertEqual(report["tool_name"], "file")
        self.assertTrue(report["proposed_fix"])


if __name__ == "__main__":
    unittest.main()
