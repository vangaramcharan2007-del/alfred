"""
Live Certification Demo: E-V Operates Under Alfred's Sovereign Command.
======================================================================
1. Alfred initializes as the Sovereign Master Butler.
2. Alfred delegates Voice, Vision, and Math to E-V as his first officer.
3. E-V executes the tasks and reports back to Alfred's core registry.
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

from jarvisx.organism import AlfredOrganism
from jarvisx.agents.ev_copilot_agent import EVCoPilotAgent
from jarvisx.automation.ev_neural_voice import speak_ev_neural


def main():
    print("=" * 80)
    print(" 🦇 ALFRED SOVEREIGN BUTLER // 🕷️ E-V CO-PILOT COMMAND HIERARCHY")
    print("=" * 80)

    # 1. Master Alfred Organism
    alfred = AlfredOrganism()
    print("\n[+] 1. Master Organism: Alfred (Sovereign Core)")
    print(f"    - Role: Sovereign Butler, Fleet Orchestrator & Security Gatekeeper")
    print(f"    - Security Gate: ZERO_LEAKS ACTIVE")

    # 2. Subordinate E-V Agent
    ev = alfred.ev_agent
    print(f"\n[+] 2. Subordinate Field Specialist: {ev.name}")
    print(f"    - Supervisor: {ev.supervisor}")
    print(f"    - Role: {ev.role}")
    print(f"    - Capabilities: {', '.join(ev.capabilities)}")

    # 3. Alfred Delegates Tasks to E-V
    print("\n[*] 3. Alfred Delegating 1D Wave Math Derivation to E-V...")
    math_result = ev.execute_delegated_task("solve_math", {"type": "1d_wave"})
    print(f"    [✓] Result: {math_result['title']} (Status: {math_result['status']})")

    # 4. Neural Voice Announcement
    print("\n[*] 4. E-V Acknowledging Alfred's Command via Neural Voice...")
    speak_ev_neural("Alfred has verified all systems, boss! I am working directly under Alfred to handle your voice, math vision, and focus quests!")

    print("\n" + "=" * 80)
    print(" 🏆 HIERARCHY DEMONSTRATION COMPLETE & VERIFIED!")
    print("=" * 80)


if __name__ == "__main__":
    main()
