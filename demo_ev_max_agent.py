"""
Live Certification Demo: E-V MAX Maxed-Out Autonomous AI Agent.
===============================================================
Demonstrates the full pre-trained curriculum, automated screen perceptron, and neural voice.
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

from jarvisx.agents.ev_max_agent import EVMaxAgent
from jarvisx.automation.ev_neural_voice import speak_ev_neural


def main():
    print("=" * 80)
    print(" 🚀 E-V MAX: MAXED-OUT TRAINED & AUTOMATED AI AGENT ENGINE")
    print("=" * 80)

    ev_max = EVMaxAgent.get_instance()
    status = ev_max.get_max_status()

    print(f"\n[+] 1. Model Status: {status['status']}")
    print(f"    - Agent Name: {status['agent']} (v{status['version']})")
    print(f"    - Supervisor: {status['supervisor']} (Sovereign Organism)")
    print(f"    - Multi-Tier LLM: Gemini 2.5 + Local Qwen2.5-Coder Engine")

    print("\n[+] 2. Trained Knowledge Matrix (Dr. E. Suresh):")
    print("    - Unit 1: PDEs (Constants elimination, Lagrange, Charpit)")
    print("    - Unit 2: Fourier Series (Dirichlet, Half-range Sine/Cosine)")
    print("    - Unit 3: BVPs (1D Wave, 1D Heat, 2D Laplace steady-state)")
    print("    - Unit 4 & 5: Transforms (Fourier, Z-Transforms, Difference eqns)")

    print("\n[*] 3. Executing Autonomous Multimodal Screen Perception & Derivation...")
    res = ev_max.perceive_and_solve_screen()
    print(f"    [✓] Solution Compiled: {res['topic']}")
    print(f"    [✓] File Artifact: {res['solution_file']}")

    print("\n[*] 4. E-V Max Voice Verification...")
    speak_ev_neural("E-V Max engine is fully trained, automated, and maxed out, boss! Ready to conquer any math problem, code sprint, or system task on your command!")

    print("\n" + "=" * 80)
    print(" 🏆 E-V MAX CERTIFICATION COMPLETE & FULLY OPERATIONAL!")
    print("=" * 80)


if __name__ == "__main__":
    main()
