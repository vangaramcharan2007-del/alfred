from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import threading
from typing import Any

from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event

def _message(event: Event) -> str:
    return str(event.payload.get("message", "")).strip()

def speak_offline(text: str, voice_gender="female"):
    if os.environ.get("JARVIS_SPEAK_OFFLINE", "").lower() not in {"1", "true", "yes"}:
        return
    if importlib.util.find_spec("pyttsx3") is None:
        return

    preferred_voice = "Zira" if voice_gender == "female" else "David"
    script = (
        "import sys, pyttsx3\n"
        "engine = pyttsx3.init()\n"
        "voices = engine.getProperty('voices')\n"
        f"preferred_voice = {preferred_voice!r}\n"
        "for v in voices:\n"
        "    if preferred_voice in v.name or preferred_voice.lower() in v.name.lower():\n"
        "        engine.setProperty('voice', v.id)\n"
        "        break\n"
        "engine.setProperty('rate', 170)\n"
        "engine.say(sys.stdin.read())\n"
        "engine.runAndWait()\n"
    )

    def run() -> None:
        subprocess.run(
            [sys.executable, "-c", script],
            input=text.encode("utf-8"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    threading.Thread(target=run, daemon=True, name="JarvisFridaySpeech").start()

class FridayAgent(BaseAgent):
    agent_id = "friday"
    role = "Execution specialist and coding assistant"
    expertise = ("execution", "coding", "desktop actions", "teaching")
    tone = "friendly, calm, and confident"
    personality = "helpful assistant"
    capabilities = ("file.read", "file.write", "file.edit", "computer.run_command")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_path = Path("assets/prompts/friday.md")
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return "You are Friday, the execution specialist of Jarvis X."

    async def handle(self, event: Event) -> AgentResponse:
        file_system = self.tools.get("file")
        computer = self.tools.get("computer")
        vscode = self.tools.get("vscode")
        text = _message(event).lower()
        
        from jarvisx.core.state import get_agent_state, update_agent_state
        import asyncio
        import os
        import subprocess
        import json
        
        action_taken = ""
        
        # Check if we need to greet
        greeting = ""
        if not get_agent_state("friday").get("friday_greeted", False):
            greeting = "Hello. I'm Friday. I'm ready to assist.\n\n"
            speak_offline("Hello. I'm Friday. I'm ready to assist.", "female")
            update_agent_state("friday", "friday_greeted", True)
            
        demo_mode = False
        config_path = os.path.join("config", "demo.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    demo_mode = config.get("demo_mode", False)
            except:
                pass

        current_stage = get_agent_state("friday").get("mission_stage", "idle")
        attempts = get_agent_state("friday").get("correction_attempts", 0)
        
        if any(kw in text for kw in ["numpy", "files", "codes", "basics"]):
            update_agent_state("friday", "mission_stage", "writing")
            update_agent_state("friday", "correction_attempts", 0)
            
            action_taken = "On it. Writing the NumPy scripts.\n"
            speak_offline("On it. Writing the Numpy scripts now.", "female")
            
            if file_system and vscode:
                try:
                    file_system.write_file("JarvisX_Tutorials/numpy_basics.py", "")
                    file_system.write_file("JarvisX_Tutorials/numpy_random.py", "")
                    
                    settings_content = "{\n    \"editor.autoClosingBrackets\": \"never\",\n    \"editor.autoClosingQuotes\": \"never\",\n    \"editor.autoIndent\": \"none\"\n}"
                    file_system.write_file("JarvisX_Tutorials/.vscode/settings.json", settings_content)
                    
                    target_path = os.path.abspath("jarvis_workspace/JarvisX_Tutorials")
                    vscode.vscode_open_workspace(target_path)
                    
                    # 1. numpy_basics.py
                    vscode.vscode_open_file(os.path.join(target_path, "numpy_basics.py"))
                    vscode.vscode_type_code(
                        "import numpy as np\n\n"
                        "# Create arrays\n"
                        "arr1 = np.array([10, 20, 30, 40, 50, 60])\n"
                        "arr2 = np.array([[1, 2, 3],\n"
                        "                 [4, 5, 6]])\n\n"
                        "# Array Basics\n"
                        "print(\"1D Array:\", arr1)\n"
                        "print(\"2D Array:\\n\", arr2)\n\n"
                        "print(\"Shape of arr2:\", arr2.shape)\n"
                        "print(\"Dimensions of arr2:\", arr2.ndim)\n"
                        "print(\"Size of arr2:\", arr2.size)\n"
                        "print(\"Data Type:\", arr2.dtype)\n\n"
                        "# Indexing\n"
                        "print(\"\\nFirst Element:\", arr1[0])\n"
                        "print(\"Last Element:\", arr1[-1])\n\n"
                        "# Slicing\n"
                        "print(\"Elements from index 1 to 4:\", arr1[1:5])\n"
                        "print(\"First Three Elements:\", arr1[:3])\n"
                        "print(\"Elements from index 3 onwards:\", arr1[3:])\n"
                        "print(\"Every Second Element:\", arr1[::2])\n\n"
                        "# 2D Array Indexing and Slicing\n"
                        "print(\"\\nElement at row 1, column 2:\", arr2[1, 2])\n"
                        "print(\"First Row:\", arr2[0])\n"
                        "print(\"Second Column:\", arr2[:, 1])\n"
                        "print(\"First Two Columns:\\n\", arr2[:, :2])\n"
                    )
                    vscode.vscode_save()
                    
                    # 2. numpy_random.py WITH INTENTIONAL BUG
                    vscode.vscode_open_file(os.path.join(target_path, "numpy_random.py"))
                    vscode.vscode_type_code(
                        "import nump as np\n\n"
                        "# 1. Random integer\n"
                        "print(\"Random Integer:\")\n"
                        "print(np.random.randint(1, 100))\n\n"
                        "# 2. Random float\n"
                        "print(\"\\nRandom Float:\")\n"
                        "print(np.random.rand())\n\n"
                        "# 3. Random 1D array\n"
                        "print(\"\\nRandom 1D Array:\")\n"
                        "print(np.random.randint(1, 50, size=5))\n\n"
                        "# 4. Random 2D array\n"
                        "print(\"\\nRandom 2D Array:\")\n"
                        "print(np.random.randint(1, 100, size=(3, 3)))\n\n"
                        "# 5. Random choice\n"
                        "print(\"\\nRandom Choice:\")\n"
                        "print(np.random.choice(['Apple', 'Banana', 'Cherry']))\n\n"
                        "# 6. Random shuffle\n"
                        "arr = np.array([1, 2, 3, 4, 5])\n"
                        "np.random.shuffle(arr)\n"
                        "print(\"\\nShuffled Array:\")\n"
                        "print(arr)\n"
                    )
                    vscode.vscode_save()
                    
                    action_taken += "\nThe programs are built. I will now execute them."
                    speak_offline("The programs are built. I will now execute them.", "female")
                    update_agent_state("friday", "mission_stage", "executing")
                    
                    text = "execute"
                    current_stage = "executing"
                except Exception as e:
                    action_taken = f"I encountered an error creating the files: {str(e)}"
            else:
                action_taken = "I need file system and vscode tools to do that, Alfred."

        if current_stage == "executing" or text.strip() == "execute":
            if "Running" not in action_taken:
                action_taken += "\nRunning the scripts...\n"
                speak_offline("Running the scripts now.", "female")
                
            if vscode and computer:
                try:
                    target_script1 = os.path.abspath("jarvis_workspace/JarvisX_Tutorials/numpy_basics.py")
                    target_script2 = os.path.abspath("jarvis_workspace/JarvisX_Tutorials/numpy_random.py")
                    
                    import pyautogui
                    # Open terminal
                    pyautogui.hotkey("ctrl", "`")
                    import time; time.sleep(1.0)
                    
                    vscode.vscode_run_in_terminal(f"python {target_script1}")
                    result1 = subprocess.run(["python", target_script1], capture_output=True, text=True)
                    
                    vscode.vscode_run_in_terminal(f"python {target_script2}")
                    result2 = subprocess.run(["python", target_script2], capture_output=True, text=True)
                    
                    if result1.returncode != 0 or result2.returncode != 0:
                        update_agent_state("friday", "mission_stage", "correcting")
                        update_agent_state("friday", "last_error", result1.stderr + result2.stderr)
                        action_taken += "\nI detected an error. Analyzing the issue."
                        speak_offline("I detected an error. Analyzing the issue.", "female")
                        
                        text = "correct"
                        current_stage = "correcting"
                    else:
                        action_taken += "\nExecution complete successfully.\nGenerating explanation..."
                        speak_offline("Execution complete successfully. Generating explanation.", "female")
                        update_agent_state("friday", "mission_stage", "explaining")
                        
                        text = "explain"
                        current_stage = "explaining"
                except Exception as e:
                    action_taken += f"I encountered an error running the programs: {str(e)}"
            else:
                action_taken += "I need VSCodeController to execute programs, Alfred."

        if current_stage == "correcting" or text.strip() == "correct":
            attempts = get_agent_state("friday").get("correction_attempts", 0)
            if attempts >= 3:
                action_taken += "\nI was unable to resolve this automatically after 3 attempts. I need your input."
                update_agent_state("friday", "mission_stage", "idle")
            else:
                update_agent_state("friday", "correction_attempts", attempts + 1)
                error_msg = get_agent_state("friday").get("last_error", "")
                
                if "ModuleNotFoundError" in error_msg or "nump" in error_msg:
                    action_taken += "\nI detected an import error with 'nump'. Correcting the code now."
                    speak_offline("I detected an import typo with nump. Let me correct the code real quick.", "female")
                    
                    if vscode:
                        target_path = os.path.abspath("jarvis_workspace/JarvisX_Tutorials")
                        vscode.vscode_open_file(os.path.join(target_path, "numpy_random.py"))
                        
                        corrected_code = (
                            "import numpy as np\n\n"
                            "# 1. Random integer\n"
                            "print(\"Random Integer:\")\n"
                            "print(np.random.randint(1, 100))\n\n"
                            "# 2. Random float\n"
                            "print(\"\\nRandom Float:\")\n"
                            "print(np.random.rand())\n\n"
                            "# 3. Random 1D array\n"
                            "print(\"\\nRandom 1D Array:\")\n"
                            "print(np.random.randint(1, 50, size=5))\n\n"
                            "# 4. Random 2D array\n"
                            "print(\"\\nRandom 2D Array:\")\n"
                            "print(np.random.randint(1, 100, size=(3, 3)))\n\n"
                            "# 5. Random choice\n"
                            "print(\"\\nRandom Choice:\")\n"
                            "print(np.random.choice(['Apple', 'Banana', 'Cherry']))\n\n"
                            "# 6. Random shuffle\n"
                            "arr = np.array([1, 2, 3, 4, 5])\n"
                            "np.random.shuffle(arr)\n"
                            "print(\"\\nShuffled Array:\")\n"
                            "print(arr)\n"
                        )
                        
                        import pyautogui, time
                        # Focus the editor area first before selecting all!
                        pyautogui.hotkey("ctrl", "1")
                        time.sleep(0.5)
                        
                        pyautogui.hotkey("ctrl", "a")
                        time.sleep(0.1)
                        pyautogui.press("backspace")
                        vscode.vscode_type_code(corrected_code)
                        vscode.vscode_save()
                        
                        action_taken += "\nCode corrected. Re-executing."
                        speak_offline("Code corrected. Re-executing.", "female")
                        update_agent_state("friday", "mission_stage", "executing")
                        
                        result = subprocess.run(["python", os.path.join(target_path, "numpy_random.py")], capture_output=True, text=True)
                        # Re-focus the terminal by clicking terminal toggle twice (close then open)
                        pyautogui.hotkey("ctrl", "`")
                        time.sleep(0.5)
                        pyautogui.hotkey("ctrl", "`")
                        time.sleep(0.5)
                        vscode.vscode_run_in_terminal(f"python {os.path.join(target_path, 'numpy_random.py')}")
                        
                        if result.returncode == 0:
                            action_taken += "\nExecution complete successfully.\nGenerating explanation..."
                            speak_offline("Execution complete successfully. Generating explanation.", "female")
                            update_agent_state("friday", "mission_stage", "explaining")
                            current_stage = "explaining"
                            text = "explain"
                        else:
                            action_taken += "\nError persists. Attempting again."
                            update_agent_state("friday", "mission_stage", "correcting")

        if current_stage == "explaining" or text.strip() == "explain":
            explanation_text = (
                "NUMPY MODULES REVISION\n\n"
                "           NumPy\n"
                "             |\n"
                "  ---------------------------\n"
                "  |            |            |\n"
                " Arrays      Slicing      Random\n"
                "  |            |            |\n"
                " 1D/2D       [start:end]  randint()\n"
                " shape       [::step]     rand()\n\n"
                "Tricks & Tips:\n"
                "- Tip 1: Negative indexing (-1) gets the last element instantly.\n"
                "- Tip 2: Use .shape and .ndim to quickly understand dataset structure.\n"
                "- Tip 3: np.random.choice is great for generating synthetic categories.\n"
            )
            
            if "Here is your explanation" not in action_taken:
                 action_taken += "\nHere is your explanation.\n"
                 speak_offline("Here is the brief explanation of the NumPy arrays, slicing, and random modules. I have mapped them out for you in Notepad. Notice how easy it is to use negative indexing to get the last element instantly.", "female")
            
            if computer and vscode:
                try:
                    import os, time
                    import pygetwindow as gw
                    
                    # Use start to force OS window creation
                    os.system("start notepad")
                    time.sleep(1.5)
                    
                    # Force window activation just in case
                    try:
                        for win in gw.getWindowsWithTitle('Notepad'):
                            win.activate()
                            break
                    except Exception as e:
                        pass
                    
                    time.sleep(1.0)
                    vscode.vscode_type_code(explanation_text)
                except Exception as e:
                    action_taken += f"\n(Failed to type in Notepad: {e})"
            
            update_agent_state("friday", "mission_stage", "completed")

        elif "write a script" in text or "create a file" in text or "write code" in text:
            if file_system:
                try:
                    file_system.write_file("stub.txt", "Stub content by Friday")
                    if not action_taken:
                        action_taken = "Creating 'stub.txt'."
                except Exception as e:
                    if not action_taken:
                        action_taken = f"I encountered an error: {str(e)}"
        
        if not action_taken:
            action_taken = "Prepared a plan to execute tasks as Friday."
                
        return self._response(
            event,
            handled=True,
            message=greeting + action_taken,
            data={"workflow_request": _message(event), "system_prompt": self.system_prompt},
        )
