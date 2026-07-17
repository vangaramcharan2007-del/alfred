import time
import os
from jarvisx.core.tools.desktop import (
    DesktopPermissionManager, DesktopTrustLevel, ProcessManager, 
    WindowManager, KeyboardController, ScreenshotManager, DesktopLogger
)

def validate():
    print("=== JARVIS X DESKTOP LAYER VALIDATION ===")
    DesktopPermissionManager.set_level(DesktopTrustLevel.SYSTEM_CONTROL)
    
    # Ensure var directory exists
    os.makedirs("var", exist_ok=True)
    
    test_file = os.path.abspath("var/desktop_test.txt")
    if os.path.exists(test_file):
        os.remove(test_file)

    # Kill notepad if running to ensure a fresh state
    try:
        ProcessManager.kill_process("notepad")
    except Exception:
        pass
    
    # 1. Launch Notepad
    print("\n1. Launching Notepad")
    ProcessManager.start_process("notepad.exe")
    
    # 2. Verify process existence
    print("\n2. Verifying process existence")
    if not ProcessManager.is_running("notepad"):
        raise RuntimeError("Notepad process is not running.")
        
    time.sleep(3) # wait for window to appear
    
    # 3. Verify window focus
    print("\n3. Focusing window")
    WindowManager.focus_window("Notepad")
    time.sleep(1)
    
    # 4. Type text
    print("\n4. Typing text")
    KeyboardController.type_text("Hello Jarvis X Desktop Automation", interval=0.01)
    time.sleep(1)
    
    # 5. Save file
    print("\n5. Saving file")
    KeyboardController.hotkey('ctrl', 'shift', 's') # Force Save As dialog
    time.sleep(3) # Wait for save dialog
    KeyboardController.type_text(test_file, interval=0.01)
    time.sleep(1)
    KeyboardController.press_key('enter')
    time.sleep(2) # Wait for save to complete
    
    # Handle overwrite prompt if it appears (though we removed the file)
    
    # 6. Verify file exists
    print("\n6. Verifying file exists")
    if not os.path.exists(test_file):
        raise RuntimeError("File was not saved correctly.")
        
    # 7. Capture screenshot
    print("\n7. Capturing screenshot")
    ScreenshotManager.capture_fullscreen("var/desktop_screenshot.png")
    
    # 8. Close application
    print("\n8. Closing application")
    ProcessManager.kill_process("notepad")
    
    # 9. Verify process termination
    print("\n9. Verifying process termination")
    if ProcessManager.is_running("notepad"):
        raise RuntimeError("Notepad process is still running after kill.")
        
    print("\nDesktop Automation Layer validation successful!")

if __name__ == "__main__":
    validate()
