"""Jarvis X: Test Autonomous Action Execution."""

from __future__ import annotations
import sys
from jarvisx.automation.autonomous_action_handler import AutonomousActionHandler

def run_test():
    print("========================================================")
    print("  JARVIS X: AUTONOMOUS ACTION HANDLER TEST")
    print("========================================================\n")

    handler = AutonomousActionHandler()
    test_cases = [
        "check system status and cpu usage",
        "create file Hello from autonomous Jarvis X test suite",
        "open notepad"
    ]

    for tc in test_cases:
        print(f">> Executing: '{tc}'")
        res = handler.try_execute_action(tc)
        if res:
            print(f"   Status : {res.get('status')}")
            print(f"   Message: {res.get('message')}\n")
        else:
            print("   No action matched (routed to LLM)\n")

    print("[+] Autonomous action tests completed successfully!")

if __name__ == "__main__":
    run_test()
