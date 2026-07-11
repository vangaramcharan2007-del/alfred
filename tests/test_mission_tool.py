from __future__ import annotations

from datetime import datetime, timezone
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.tools.memory import LocalMemoryTool
from jarvisx.tools.missions import MissionTool


class MissionToolTests(unittest.TestCase):
    def test_create_mission_persists_active_main_quest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = _mission_tool(Path(temp_dir))

            created = tool.create_mission(
                "Build Edith bridge",
                "main_quest",
                progress_target=3,
                trace_id="trace-create",
            )
            active = tool.list_active_missions(trace_id="trace-create")

            self.assertTrue(created.success)
            self.assertEqual(created.data["mission"]["type"], "main_quest")
            self.assertEqual(created.data["mission"]["xp"], 100)
            self.assertEqual(len(active.data["missions"]), 1)
            self.assertEqual(active.data["missions"][0]["progress_percent"], 0)

    def test_complete_mission_awards_xp(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = _mission_tool(Path(temp_dir))
            created = tool.create_mission("Defeat config drift", "boss_fight")
            mission_id = created.data["mission"]["id"]

            completed = tool.complete_mission(mission_id, trace_id="trace-complete")

            self.assertTrue(completed.success)
            self.assertEqual(completed.data["xp_awarded"], 250)
            self.assertEqual(completed.data["stats"]["total_xp"], 250)
            self.assertEqual(completed.data["mission"]["status"], "completed")

    def test_progress_tracking_before_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = _mission_tool(Path(temp_dir))
            created = tool.create_mission("Ship three small wins", "side_quest", progress_target=3)
            mission_id = created.data["mission"]["id"]

            progressed = tool.complete_mission(mission_id, progress=1)
            active = tool.list_active_missions()

            self.assertTrue(progressed.success)
            self.assertEqual(progressed.data["xp_awarded"], 0)
            self.assertEqual(active.data["missions"][0]["progress_current"], 1)
            self.assertEqual(active.data["missions"][0]["progress_percent"], 33)

    def test_persistence_reloads_from_memory_tool(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir) / "vault"
            first_memory = LocalMemoryTool(vault_path=vault)
            first_tool = MissionTool(memory_tool=first_memory)
            first_tool.create_mission("Persist the mission log", "daily_mission")

            second_memory = LocalMemoryTool(vault_path=vault)
            second_tool = MissionTool(memory_tool=second_memory)
            active = second_tool.list_active_missions()

            self.assertTrue(active.success)
            self.assertEqual(len(active.data["missions"]), 1)
            self.assertEqual(active.data["missions"][0]["title"], "Persist the mission log")

    def test_recovery_generation_after_inactivity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            now = datetime(2026, 7, 11, tzinfo=timezone.utc)
            tool = _mission_tool(Path(temp_dir), now=now)
            created = tool.create_mission(
                "Old daily spark",
                "daily_mission",
                created_at="2026-07-08T08:00:00+00:00",
            )
            tool.complete_mission(
                created.data["mission"]["id"],
                completed_at="2026-07-08T09:00:00+00:00",
            )

            recovery = tool.generate_recovery_mission(trace_id="trace-recovery")
            active = tool.list_active_missions()

            self.assertTrue(recovery.success)
            self.assertEqual(recovery.data["mission"]["type"], "recovery_mission")
            self.assertIn("3 inactive day(s)", recovery.data["mission"]["description"])
            self.assertEqual(active.data["stats"]["inactive_days"], 3)

    def test_next_mission_prioritizes_recovery_momentum(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = _mission_tool(Path(temp_dir))
            tool.create_mission("Large boss", "boss_fight")
            recovery = tool.generate_recovery_mission(inactive_days=2)

            next_mission = tool.get_next_mission()

            self.assertTrue(next_mission.success)
            self.assertEqual(next_mission.data["mission"]["id"], recovery.data["mission"]["id"])


def _mission_tool(root: Path, *, now: datetime | None = None) -> MissionTool:
    memory = LocalMemoryTool(vault_path=root / "vault")
    return MissionTool(
        memory_tool=memory,
        now=(lambda: now) if now else None,
    )


if __name__ == "__main__":
    unittest.main()
