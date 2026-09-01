"""
Unit tests verifying E-V functions as a subordinate agent under Alfred's Command.
================================================================================
"""

import unittest
from jarvisx.agents.ev_copilot_agent import EVCoPilotAgent


class TestEVUnderAlfred(unittest.TestCase):

    def test_ev_initialization_and_supervisor(self):
        ev = EVCoPilotAgent.get_instance()
        self.assertEqual(ev.name, "E-V")
        self.assertEqual(ev.supervisor, "Alfred")
        self.assertIn("neural_voice", ev.capabilities)
        self.assertIn("screen_vision", ev.capabilities)
        self.assertIn("math_pde_solver", ev.capabilities)

    def test_alfred_delegation_math(self):
        ev = EVCoPilotAgent.get_instance()
        res = ev.execute_delegated_task("solve_math", {"type": "1d_wave"})
        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("delegated_by"), "Alfred")
        self.assertIn("Wave", res.get("title", ""))

    def test_alfred_delegation_quest(self):
        ev = EVCoPilotAgent.get_instance()
        res = ev.execute_delegated_task("adhd_quest", {"duration": 5})
        self.assertEqual(res.get("status"), "active")
        self.assertEqual(res.get("xp_reward"), 100)


if __name__ == "__main__":
    unittest.main()
