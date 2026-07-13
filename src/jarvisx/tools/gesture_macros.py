import time
import json
import os
import threading
import logging

class GestureMacroEngine:
    def __init__(self, map_file: str = "C:\\Users\\vanga\\Documents\\Jarvis_Vault\\Profiles\\macro_map.json"):
        self.map_file = map_file
        self.macro_map = {}
        self.running = False
        self._thread = None
        self._current_state = None
        self._state_start_time = 0.0
        self.debounce_seconds = 1.5
        self._load_map()

    def _load_map(self):
        try:
            os.makedirs(os.path.dirname(self.map_file), exist_ok=True)
            if os.path.exists(self.map_file):
                with open(self.map_file, "r") as f:
                    self.macro_map = json.load(f)
            else:
                self.macro_map = {
                    "thumbs_up": {"action": "bring_to_foreground", "target": "Spotify"},
                    "peace_sign": {"action": "bring_to_foreground", "target": "Visual Studio Code"}
                }
                with open(self.map_file, "w") as f:
                    json.dump(self.macro_map, f, indent=4)
        except Exception as e:
            logging.error(f"GestureMacroEngine init fault: {e}")

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._macro_loop, daemon=True)
        # Sleep throttling keeps CPU load extremely low simulating low-priority
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _macro_loop(self):
        while self.running:
            try:
                # Simulated polling of vision/biometric state
                detected_gesture = self._poll_vision_engine()
                
                if detected_gesture != self._current_state:
                    self._current_state = detected_gesture
                    self._state_start_time = time.time()
                elif detected_gesture and (time.time() - self._state_start_time) >= self.debounce_seconds:
                    self._execute_macro(detected_gesture)
                    # Reset to avoid infinite loop firing
                    self._state_start_time = time.time() + 5.0 
                    
                # Throttled polling loop
                time.sleep(0.5)
            except Exception as e:
                logging.error(f"Macro loop fault: {e}")

    def _poll_vision_engine(self) -> str | None:
        # In a real scenario, this queries the active cv2/biometric frame buffer
        return None

    def _execute_macro(self, gesture: str):
        if gesture in self.macro_map:
            action = self.macro_map[gesture]
            logging.info(f"Executing gesture macro: {gesture} -> {action}")
            # Dispatch to win_control.py based on action payload
            try:
                from src.jarvisx.tools.win_control import WinController
                controller = WinController()
                if action.get("action") == "bring_to_foreground":
                    controller.safe_bring_to_foreground(action.get("target"))
            except Exception as e:
                logging.error(f"Gesture macro execution failed: {e}")
