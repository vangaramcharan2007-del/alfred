import sys
import os

with open(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\src\jarvisx\agents\friday.py", "r") as f:
    code = f.read()

# 1. Update numpy_random.py code generation to include >= 5 operations
old_random_code = """                    vscode.vscode_type_code(
                        "import nump as np\\n\\n"
                        "# Random integer\\n"
                        "print(\\\"Random Integer:\\\")\\n"
                        "print(np.random.randint(1, 100))\\n\\n"
                        "# Random float\\n"
                        "print(\\\"\\\\nRandom Float:\\\")\\n"
                        "print(np.random.rand())\\n\\n"
                        "# Random 1D array\\n"
                        "print(\\\"\\\\nRandom 1D Array:\\\")\\n"
                        "print(np.random.randint(1, 50, size=5))\\n\\n"
                        "# Random 2D array\\n"
                        "print(\\\"\\\\nRandom 2D Array:\\\")\\n"
                        "print(np.random.randint(1, 100, size=(3, 3)))\\n"
                    )"""

new_random_code = """                    vscode.vscode_type_code(
                        "import nump as np\\n\\n"
                        "# 1. Random integer\\n"
                        "print(\\\"Random Integer:\\\")\\n"
                        "print(np.random.randint(1, 100))\\n\\n"
                        "# 2. Random float\\n"
                        "print(\\\"\\\\nRandom Float:\\\")\\n"
                        "print(np.random.rand())\\n\\n"
                        "# 3. Random 1D array\\n"
                        "print(\\\"\\\\nRandom 1D Array:\\\")\\n"
                        "print(np.random.randint(1, 50, size=5))\\n\\n"
                        "# 4. Random 2D array\\n"
                        "print(\\\"\\\\nRandom 2D Array:\\\")\\n"
                        "print(np.random.randint(1, 100, size=(3, 3)))\\n\\n"
                        "# 5. Random choice\\n"
                        "print(\\\"\\\\nRandom Choice:\\\")\\n"
                        "print(np.random.choice(['Apple', 'Banana', 'Cherry']))\\n\\n"
                        "# 6. Random shuffle\\n"
                        "arr = np.array([1, 2, 3, 4, 5])\\n"
                        "np.random.shuffle(arr)\\n"
                        "print(\\\"\\\\nShuffled Array:\\\")\\n"
                        "print(arr)\\n"
                    )"""

code = code.replace(old_random_code, new_random_code)

# Update the correcting block with the same 5+ operations (but with 'numpy' instead of 'nump')
old_corrected_code = """                        corrected_code = (
                            "import numpy as np\\n\\n"
                            "# Random integer\\n"
                            "print(\\\"Random Integer:\\\")\\n"
                            "print(np.random.randint(1, 100))\\n\\n"
                            "# Random float\\n"
                            "print(\\\"\\\\nRandom Float:\\\")\\n"
                            "print(np.random.rand())\\n\\n"
                            "# Random 1D array\\n"
                            "print(\\\"\\\\nRandom 1D Array:\\\")\\n"
                            "print(np.random.randint(1, 50, size=5))\\n\\n"
                            "# Random 2D array\\n"
                            "print(\\\"\\\\nRandom 2D Array:\\\")\\n"
                            "print(np.random.randint(1, 100, size=(3, 3)))\\n"
                        )"""

new_corrected_code = """                        corrected_code = (
                            "import numpy as np\\n\\n"
                            "# 1. Random integer\\n"
                            "print(\\\"Random Integer:\\\")\\n"
                            "print(np.random.randint(1, 100))\\n\\n"
                            "# 2. Random float\\n"
                            "print(\\\"\\\\nRandom Float:\\\")\\n"
                            "print(np.random.rand())\\n\\n"
                            "# 3. Random 1D array\\n"
                            "print(\\\"\\\\nRandom 1D Array:\\\")\\n"
                            "print(np.random.randint(1, 50, size=5))\\n\\n"
                            "# 4. Random 2D array\\n"
                            "print(\\\"\\\\nRandom 2D Array:\\\")\\n"
                            "print(np.random.randint(1, 100, size=(3, 3)))\\n\\n"
                            "# 5. Random choice\\n"
                            "print(\\\"\\\\nRandom Choice:\\\")\\n"
                            "print(np.random.choice(['Apple', 'Banana', 'Cherry']))\\n\\n"
                            "# 6. Random shuffle\\n"
                            "arr = np.array([1, 2, 3, 4, 5])\\n"
                            "np.random.shuffle(arr)\\n"
                            "print(\\\"\\\\nShuffled Array:\\\")\\n"
                            "print(arr)\\n"
                        )"""
                        
code = code.replace(old_corrected_code, new_corrected_code)

# 2. Fix the Notepad opening logic to guarantee focus
old_notepad_logic = """            if computer and vscode:
                try:
                    computer.run_command("notepad", _user_approved=True)
                    import time
                    time.sleep(1.5)
                    vscode.vscode_type_code(explanation_text)"""
                    
new_notepad_logic = """            if computer and vscode:
                try:
                    import os, time
                    # Use start to aggressively push Notepad to front in Windows
                    os.system("start notepad")
                    time.sleep(2.5) # Give it ample time to open and grab focus
                    vscode.vscode_type_code(explanation_text)"""

code = code.replace(old_notepad_logic, new_notepad_logic)

with open(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\src\jarvisx\agents\friday.py", "w") as f:
    f.write(code)

print("Friday.py updated successfully.")
