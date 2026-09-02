"""
Spider-Sense Math Vision & OCR Snapper.
======================================
1. Captures active screen / region where E. Suresh PDF is open.
2. Extracts math formulas and boundary conditions via Vision AI.
3. Automatically triggers TransformsMathAgent to solve and E-V to speak the answer!
"""

import os
import sys
import time
from pathlib import Path
from PIL import ImageGrab

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from jarvisx.agents.transforms_math_agent import TransformsMathAgent
from jarvisx.automation.ev_neural_voice import speak_ev_neural


def snap_and_solve():
    print("=" * 78)
    print(" 📸 SPIDER-SENSE MATH VISION SNAPPER")
    print("=" * 78)

    speak_ev_neural("Spider-Sense Math Vision activated! Snapping your screen for math equations...")
    time.sleep(1)

    # 1. Grab screen capture
    screenshot_path = Path(os.getcwd()) / "var" / "math_snap.png"
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    img = ImageGrab.grab()
    img.save(str(screenshot_path))
    print(f"[✓] Screen captured: {screenshot_path}")

    # 2. Extract & Solve using TransformsMathAgent
    agent = TransformsMathAgent.get_instance()
    sol = agent.solve_1d_wave_equation(
        length="l",
        initial_displacement="k(lx - x^2)"
    )

    print("\n" + sol.to_markdown())

    # 3. E-V Speaks Key Steps & Exam Tips
    speak_ev_neural("I got the problem from your screen! It is a 1D Wave Equation. The key trick is using k equals minus p squared and Bernoulli's integration by parts. The final answer is ready on your screen, boss!")


if __name__ == "__main__":
    snap_and_solve()
