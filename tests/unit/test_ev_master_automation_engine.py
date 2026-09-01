"""
Unit tests for E-V Master 5-Level Autonomous Automation Engine.
==============================================================
Verifies Levels 1, 2, 3, 4, and 5 execution under Alfred's Sovereign Gate.
"""

import unittest
from jarvisx.automation.ev_master_automation_engine import EVMasterAutomationEngine


class TestEVMasterAutomationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = EVMasterAutomationEngine.get_instance()

    def test_level_1_hotkey_action(self):
        res = self.engine.level_1_hotkey_action("F8")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["level"], 1)

    def test_level_2_screen_vision(self):
        res = self.engine.level_2_screen_vision_solve()
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["level"], 2)
        self.assertIn("Wave", res["topic"])

    def test_level_3_proactive_watcher(self):
        res = self.engine.level_3_start_proactive_watcher(check_interval_sec=10)
        self.assertIn(res["status"], ["active", "already_running"])
        self.assertEqual(res["level"], 3)
        self.engine.level_3_stop_proactive_watcher()

    def test_level_4_whatsapp_bridge(self):
        res = self.engine.level_4_process_whatsapp_inbound("Please solve 1D Heat Equation from E. Suresh")
        self.assertEqual(res["status"], "delivered")
        self.assertEqual(res["level"], 4)
        self.assertEqual(res["target_phone"], "+91 8074881520")
        self.assertTrue(res["voice_note_ready"])

    def test_level_5_turbo_cool(self):
        res = self.engine.level_5_turbo_cool()
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["level"], 5)

    def test_full_suite_audit(self):
        audit = self.engine.run_full_suite_audit()
        self.assertEqual(audit["status"], "ALL_LEVELS_COMPLETED_AND_ACTIVE")
        self.assertEqual(len(audit["levels"]), 5)


if __name__ == "__main__":
    unittest.main()
