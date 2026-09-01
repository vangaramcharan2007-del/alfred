"""
Live Demonstration of TransformsMathAgent (Dr. E. Suresh M3 Curriculum).
========================================================================
Runs real live math derivations for Boundary Value Problems with E-V Neural Voice narration!
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from jarvisx.agents.transforms_math_agent import TransformsMathAgent


def main():
    print("=" * 80)
    print(" 📐 TRANSFORMS & BOUNDARY VALUE PROBLEMS AGENT (E. SURESH MATH TUTOR)")
    print("=" * 80)

    agent = TransformsMathAgent.get_instance()

    print("\n[+] SOLVING: 1D Wave Equation (Vibrating String with Fixed Ends)")
    sol_wave = agent.solve_1d_wave_equation(
        length="l",
        initial_displacement="k(lx - x^2)",
        initial_velocity="0"
    )
    print(sol_wave.to_markdown())

    print("\n" + "=" * 80)
    print("[+] SOLVING: 1D Heat Equation (Homogeneous Rod with Zero Temperature Ends)")
    print("=" * 80)
    sol_heat = agent.solve_1d_heat_equation(
        length="l",
        initial_temp="100"
    )
    print(sol_heat.to_markdown())

    # Speak voice summary via E-V
    print("\n[*] Triggering E-V Neural Voice Exam Walkthrough...")
    agent.explain_with_ev_voice("Hey boss! I solved both the 1D Wave Equation and 1D Heat Conduction problem from E. Suresh! Check out the clean step-by-step Fourier expansions on your screen!")

    print("\n" + "=" * 80)
    print(" 🏆 TRANSFORMS MATH AGENT CERTIFICATION COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
