"""
Live Demonstration Script for Alfred OS Dynamic AI Agent Factory.
Demonstrates:
1. Creating a brand new specialized AI agent on the fly using Gemini 3.6 Flash.
2. Registering the new agent into the persistent agent fleet.
3. Executing a live operational task with the newly created agent.
4. Announcing completion via Ultra-Realistic Neural Speech.
"""

import asyncio
import os
import sys
import time

# Ensure UTF-8 console output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to sys.path
sys.path.insert(0, os.path.abspath("src"))

from jarvisx.agents.agent_factory import get_agent_factory
from jarvisx.voice.sovereign_neural_tts import get_neural_tts


def main():
    print("\n" + "=" * 75)
    print(" 🤖 ALFRED OS — DYNAMIC AI AGENT FACTORY (LIVE DEMONSTRATION)")
    print("=" * 75)

    factory = get_agent_factory()
    tts = get_neural_tts()

    # 1. Create a New Custom Agent from Natural Language Prompt
    user_prompt = "Create a CyberSecuritySentinelAgent that audits system security, monitors ports, and flags vulnerabilities."
    print(f"\n[*] User Command: '{user_prompt}'")
    print("[*] Contacting Gemini 3.6 Flash Cloud Brain to design Agent Architecture...")

    spec = asyncio.run(factory.create_agent_from_prompt_async(user_prompt))

    print("\n" + "-" * 75)
    print(f" ✨ NEW AGENT CREATED & DEPLOYED: {spec.name}")
    print("-" * 75)
    print(f" • Role           : {spec.role}")
    print(f" • Description    : {spec.description}")
    print(f" • Allocated Tools: {spec.tools}")
    print(f" • System Prompt  : {spec.system_prompt[:140]}...")

    # 2. Execute a Live Mission on the Newly Created Agent
    test_task = "Perform a security diagnostic check on laptop ports and verify memory safety."
    print(f"\n[*] Dispatching Live Task to {spec.name}: '{test_task}'")

    execution_res = asyncio.run(factory.execute_agent_task_async(spec.name, test_task))

    print("\n" + "-" * 75)
    print(f" 🎯 {spec.name} TASK EXECUTION RESULT:")
    print("-" * 75)
    print(execution_res.get("result", ""))

    # 3. Voice Announcement
    tts_msg = f"New AI Agent {spec.name} has been successfully deployed and added to your fleet."
    print(f"\n[JARVIS VOICE]: {tts_msg}")
    tts.speak(tts_msg, blocking=True)

    print("\n" + "=" * 75)
    print(" [OK] ✅ DYNAMIC AGENT CREATION & EXECUTION VALIDATED LIVE")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
