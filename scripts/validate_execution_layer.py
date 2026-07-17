import sys
import os
from jarvisx.core.tools.execution import (
    CommandExecutor,
    AppLauncher,
    FileOps,
    PythonExecutor,
    GitOps
)

def validate():
    print("=== JARVIS X EXECUTION LAYER VALIDATION ===")
    
    print("\n1. Create and execute hello.py")
    FileOps.write_file("hello.py", 'print("Hello Jarvis")')
    res = PythonExecutor.execute('print("Hello Jarvis")')
    print(f"Python Output: {res['stdout']}")
    
    print("\n2. Create and delete temporary file")
    FileOps.create_file("test_temp.txt", "Temp Content")
    print(f"File exists: {os.path.exists('test_temp.txt')}")
    FileOps.delete_file("test_temp.txt")
    print(f"File deleted: {not os.path.exists('test_temp.txt')}")
    
    print("\n3. Git Operations")
    print(f"Git Status: \n{GitOps.status()}")
    FileOps.write_file("git_temp.txt", "Git test file")
    GitOps.add("git_temp.txt")
    print("Added git_temp.txt to staging")
    
    print("\n4. Open Notepad")
    success = AppLauncher.launch("notepad")
    print(f"Notepad launched: {success}")
    
    print("\n5. List running processes")
    print(f"Notepad is running: {AppLauncher.is_running('notepad')}")
    
    print("\n6. Close Notepad")
    AppLauncher.close("notepad")
    print(f"Notepad closed.")
    
    print("\n7. Cleanup")
    FileOps.delete_file("hello.py")
    FileOps.delete_file("git_temp.txt")

if __name__ == "__main__":
    validate()
