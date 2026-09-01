"""
Unit tests for E-V MAX Maxed-Out Autonomous Agent.
=================================================
"""

import unittest
from jarvisx.agents.ev_max_agent import EVMaxAgent, EVMaxKnowledgeBase


class TestEVMaxAgent(unittest.TestCase):

    def test_ev_max_initialization(self):
        ev = EVMaxAgent.get_instance()
        status = ev.get_max_status()
        self.assertEqual(status["agent"], "E-V MAX")
        self.assertEqual(status["supervisor"], "Alfred")
        self.assertEqual(status["status"], "MAXED_OUT_AND_AUTOMATED")
        self.assertIn("sympy_exact_math_proofs", status["capabilities"])

    def test_ev_max_knowledge_base(self):
        kb = EVMaxKnowledgeBase()
        self.assertIn("z=(x-a)^2+(y-b)^2", kb.UNIT_1_PDES["standard_solutions"])
        self.assertEqual(kb.UNIT_1_PDES["standard_solutions"]["z=(x-a)^2+(y-b)^2"], "4z = p^2 + q^2")
        self.assertIn("1D_Wave", kb.UNIT_3_BVPS["equations"])
        self.assertIn("1D_Heat", kb.UNIT_3_BVPS["equations"])

    def test_ev_max_adhd_quest(self):
        ev = EVMaxAgent.get_instance()
        res = ev.launch_adhd_micro_quest(duration_sec=300)
        self.assertEqual(res["status"], "active")
        self.assertEqual(res["xp_reward"], 150)


if __name__ == "__main__":
    unittest.main()
