from __future__ import annotations

import asyncio
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvisx.runtime import create_default_runtime
from jarvisx.tools.memory import LocalMemoryTool
from jarvisx.tools.missions import MissionTool
from jarvisx.tools.operational_db import OperationalDatabase
from jarvisx.tools.personalization import PersonalizationTool


class PersonalizationToolTests(unittest.TestCase):
    def test_mode_switching(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = _personalization_tool(Path(temp_dir))

            result = tool.set_mode("focus", trace_id="trace-mode")
            active = tool.get_mode(trace_id="trace-mode")

            self.assertTrue(result.success)
            self.assertEqual(active.data["mode"]["mode"], "focus")
            self.assertEqual(active.data["mode"]["response_length"], "short")

    def test_invalid_mode_handling_preserves_current_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = _personalization_tool(Path(temp_dir))
            tool.set_mode("study")

            invalid = tool.set_mode("chaos")
            active = tool.get_mode()

            self.assertFalse(invalid.success)
            self.assertEqual(active.data["mode"]["mode"], "study")

    def test_personality_persistence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir) / "vault"
            first = PersonalizationTool(
                memory_tool=LocalMemoryTool(vault_path=vault),
                config_manager=ConfigurationManager(OperationalDatabase(db_path=vault / "op.db"))
            )
            first.set_personality(
                "research",
                {"tone": "curious teacher", "style": "methodical with citations"},
                trace_id="trace-personality",
            )

            second = PersonalizationTool(
                memory_tool=LocalMemoryTool(vault_path=vault),
                config_manager=ConfigurationManager(OperationalDatabase(db_path=vault / "op.db"))
            )
            loaded = second.get_personality("research")

            self.assertTrue(loaded.success)
            self.assertEqual(loaded.data["personality"]["agent_id"], "research")
            self.assertEqual(loaded.data["personality"]["tone"], "curious teacher")

    def test_startup_restoration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir) / "vault"
            first = PersonalizationTool(
                memory_tool=LocalMemoryTool(vault_path=vault),
                config_manager=ConfigurationManager(OperationalDatabase(db_path=vault / "op.db"))
            )
            first.set_mode("builder")

            restored = PersonalizationTool(
                memory_tool=LocalMemoryTool(vault_path=vault),
                config_manager=ConfigurationManager(OperationalDatabase(db_path=vault / "op.db"))
            )

            self.assertEqual(restored.get_mode().data["mode"]["mode"], "builder")

    def test_agent_specific_personality_retrieval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = _personalization_tool(Path(temp_dir))

            alfred = tool.get_personality("alfred")
            hermes = tool.get_personality("hermes")
            future = tool.get_personality("new_agent")

            self.assertEqual(alfred.data["personality"]["name"], "Alfred")
            self.assertEqual(hermes.data["personality"]["agent_id"], "hermes")
            self.assertEqual(future.data["personality"]["agent_id"], "new_agent")

    def test_mode_influences_response_configuration_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = _personalization_tool(Path(temp_dir))
            tool.set_mode("emergency")

            config = tool.get_response_config("alfred")

            self.assertTrue(config.data["style_only"])
            self.assertEqual(config.data["mode"]["mode"], "emergency")
            self.assertEqual(config.data["mode"]["detail_level"], "critical_only")
            self.assertFalse(config.data["logic_boundaries"]["affects_routing"])
            self.assertFalse(config.data["logic_boundaries"]["affects_permissions"])
            self.assertFalse(config.data["logic_boundaries"]["affects_execution"])

    def test_personality_rejects_logic_affecting_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tool = _personalization_tool(Path(temp_dir))

            result = tool.set_personality(
                "alfred",
                {"tone": "direct", "routing": "always choose device"},
            )

            self.assertFalse(result.success)
            self.assertIn("routing", result.data["forbidden_fields"])

    def test_routing_behavior_remains_unchanged_by_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = create_default_runtime(
                log_path=root / "jarvisx.jsonl",
                obsidian_vault=root / "vault",
            )
            runtime.personalization.set_mode("study", trace_id="trace-route")

            response = asyncio.run(
                runtime.alfred.process("Open YouTube", trace_id="trace-route")
            )

            self.assertTrue(response.handled)
            self.assertEqual(response.agent_id, "device")
            self.assertEqual(response.data["intent"]["agent_id"], "device")
            self.assertEqual(response.data["response_config"]["mode"]["mode"], "study")
            self.assertFalse(response.data["response_config"]["logic_boundaries"]["affects_routing"])

    def test_edith_uses_agent_specific_response_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = create_default_runtime(
                log_path=root / "jarvisx.jsonl",
                obsidian_vault=root / "vault",
            )
            runtime.personalization.set_mode("focus", trace_id="trace-edith")

            response = asyncio.run(
                runtime.alfred.process("voice notification status", trace_id="trace-edith")
            )

            self.assertTrue(response.handled)
            self.assertEqual(response.agent_id, "edith")
            self.assertEqual(response.data["response_config"]["personality"]["agent_id"], "edith")
            self.assertEqual(response.data["response_config"]["mode"]["mode"], "focus")
            self.assertEqual(
                response.data["orchestrator_response_config"]["personality"]["agent_id"],
                "alfred",
            )

    def test_mission_prioritization_uses_current_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            memory = LocalMemoryTool(vault_path=root / "vault")
            personalization = PersonalizationTool(
                memory_tool=memory,
                config_manager=ConfigurationManager(OperationalDatabase(db_path=root / "vault" / "op.db"))
            )
            missions = MissionTool(memory_tool=memory, personalization_tool=personalization)
            daily = missions.create_mission("Daily review", "daily_mission")
            boss = missions.create_mission("Refactor core runtime", "boss_fight")

            default_next = missions.get_next_mission()
            personalization.set_mode("builder")
            builder_next = missions.get_next_mission()

            self.assertEqual(default_next.data["mission"]["id"], daily.data["mission"]["id"])
            self.assertEqual(builder_next.data["mission"]["id"], boss.data["mission"]["id"])
            self.assertEqual(builder_next.data["mission"]["mode_priority_boost"], 15)


from jarvisx.core.configuration import ConfigurationManager

def _personalization_tool(root: Path) -> PersonalizationTool:
    return PersonalizationTool(
        memory_tool=LocalMemoryTool(vault_path=root / "vault"),
        config_manager=ConfigurationManager(OperationalDatabase(db_path=root / "vault" / "op.db"))
    )


if __name__ == "__main__":
    unittest.main()
