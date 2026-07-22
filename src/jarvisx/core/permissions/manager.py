from typing import Any
import sys
import os

class PermissionManager:
    """
    Core trust layer. Intercepts capability execution to request user permission
    before modifying the OS or launching side-effects.
    """
    
    # Actions that don't require explicit user confirmation
    SAFE_ACTIONS = {
        "read",
        "summarize",
        "search", 
        "evaluate"
    }

    def __init__(self, dashboard=None):
        self.dashboard = dashboard
        # Check if running in automated test/harness environment
        self.is_harness = os.environ.get("MOCK_STT") == "1"

    def request(self, action: str, target: str, voice_prompt_callback: Any = None) -> bool:
        """
        Determines if an action requires permission, and if so, prompts the user.
        If voice_prompt_callback is provided, it calls it to await spoken permission.
        """
        action_lower = action.lower()
        if action_lower in self.SAFE_ACTIONS:
            return True

        if self.is_harness:
            # In automated tests, auto-approve to not block execution
            return True

        # Need approval
        prompt_text = f"Alfred wants to {action} {target}. Should I proceed?"
        
        # If running in Voice Mode
        if voice_prompt_callback:
            if self.dashboard:
                self.dashboard.set_tts(prompt_text)
                self.dashboard.render()
            print(f"\n[PERMISSION REQUIRED] {prompt_text}")
            return voice_prompt_callback(prompt_text)
            
        # In a generic terminal Mode
        if self.dashboard:
            self.dashboard.set_tts(prompt_text)
            self.dashboard.render()
            
        print(f"\n[PERMISSION REQUIRED]")
        print(f"{prompt_text}")
        
        while True:
            try:
                response = input("(y/n): ").strip().lower()
                if response in ('y', 'yes'):
                    if self.dashboard:
                        self.dashboard.set_tts("Permission granted.")
                    return True
                elif response in ('n', 'no'):
                    if self.dashboard:
                        self.dashboard.set_tts("Permission denied.")
                    return False
                else:
                    print("Please answer y or n.")
            except (EOFError, KeyboardInterrupt):
                # If running in a pipe where input is closed or user interrupts
                return False
