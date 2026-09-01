"""
Unit tests for TransformsMathAgent (Dr. E. Suresh Curriculum).
=============================================================
Verifies 1D Wave Equation, 1D Heat Equation, Fourier expansions, and LaTeX generation.
"""

import unittest
from jarvisx.agents.transforms_math_agent import TransformsMathAgent, MathSolution


class TestTransformsMathAgent(unittest.TestCase):

    def setUp(self):
        self.agent = TransformsMathAgent.get_instance()

    def test_wave_equation_solver(self):
        sol = self.agent.solve_1d_wave_equation(length="l", initial_displacement="k(lx - x^2)")
        self.assertIsInstance(sol, MathSolution)
        self.assertEqual(sol.unit, "Unit 3: Boundary Value Problems")
        self.assertIn("8k l^2", sol.final_answer)
        self.assertTrue(len(sol.solution_steps) >= 5)

    def test_heat_equation_solver(self):
        sol = self.agent.solve_1d_heat_equation(length="l", initial_temp="100")
        self.assertIsInstance(sol, MathSolution)
        self.assertIn("400", sol.final_answer)
        self.assertIn("e^{-", sol.final_answer)

    def test_markdown_generation(self):
        sol = self.agent.solve_1d_wave_equation()
        md = sol.to_markdown()
        self.assertIn("# 📐", md)
        self.assertIn("Final Answer", md)
        self.assertIn("Exam Pitfalls", md)


if __name__ == "__main__":
    unittest.main()
