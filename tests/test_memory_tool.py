from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.core.logging import StructuredLogger
from jarvisx.tools.memory import REQUIRED_DIRECTORIES, LocalMemoryTool


class MemoryToolTests(unittest.TestCase):
    def test_save_memory_writes_markdown_to_category(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir) / "vault"
            tool = LocalMemoryTool(vault_path=vault)

            result = tool.save_memory("Prefer quiet dashboards", "preference", trace_id="trace-save")

            self.assertTrue(result.success)
            record = result.data["record"]
            self.assertEqual(record["category"], "preference")
            path = vault / record["path"]
            self.assertEqual(path.parent.name, "Preferences")
            self.assertEqual(path.suffix, ".md")
            self.assertIn("Prefer quiet dashboards", path.read_text(encoding="utf-8"))

    def test_search_memory_uses_keyword_search(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = LocalMemoryTool(vault_path=Path(temp_dir) / "vault")
            tool.save_memory("Jarvis X memory stays Markdown first", "architecture")
            tool.save_memory("Use compact layouts for tools", "preference")

            result = tool.search_memory("Markdown memory", trace_id="trace-search")

            self.assertTrue(result.success)
            self.assertEqual(len(result.data["records"]), 1)
            self.assertEqual(result.data["records"][0]["category"], "architecture")

    def test_daily_notes_append_and_get(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = LocalMemoryTool(vault_path=Path(temp_dir) / "vault")

            append_result = tool.append_daily_note("Reviewed Memory v1", trace_id="trace-daily")
            get_result = tool.get_daily_note(trace_id="trace-daily")

            self.assertTrue(append_result.success)
            self.assertTrue(get_result.success)
            self.assertIn("Daily/", get_result.data["path"])
            self.assertIn("Reviewed Memory v1", get_result.data["content"])

    def test_category_routing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir) / "vault"
            tool = LocalMemoryTool(vault_path=vault)

            expectations = {
                "preference": "Preferences",
                "project": "Projects",
                "conversation": "Conversations",
                "architecture": "Architecture",
                "general": "Scratchpad",
            }
            for category, directory in expectations.items():
                result = tool.save_memory(f"{category} memory", category)
                self.assertTrue(result.success)
                self.assertEqual((vault / result.data["record"]["path"]).parent.name, directory)

            invalid = tool.save_memory("bad category", "unsupported")
            self.assertFalse(invalid.success)

    def test_vault_recovery_recreates_missing_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir) / "vault"
            tool = LocalMemoryTool(vault_path=vault)
            (vault / "Projects").rmdir()

            result = tool.save_memory("Recovered project memory", "project")

            self.assertTrue(result.success)
            for directory in REQUIRED_DIRECTORIES:
                self.assertTrue((vault / directory).is_dir())

    def test_memory_logs_reads_writes_and_failed_lookups_with_trace_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            log_path = root / "memory.jsonl"
            logger = StructuredLogger(path=log_path)
            tool = LocalMemoryTool(vault_path=root / "vault", logger=logger)

            tool.save_memory("Traceable memory", "general", trace_id="trace-log")
            tool.search_memory("missing-token", trace_id="trace-log")

            records = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
            ]
            messages = [record["message"] for record in records]
            self.assertIn("memory.write", messages)
            self.assertIn("memory.read", messages)
            self.assertIn("memory.lookup.failed", messages)
            self.assertTrue(
                all(
                    record["trace_id"] == "trace-log"
                    for record in records
                    if record["message"].startswith("memory.")
                )
            )


if __name__ == "__main__":
    unittest.main()
