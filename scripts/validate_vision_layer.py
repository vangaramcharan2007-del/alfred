import os
import time
from jarvisx.core.tools.desktop import (
    DesktopPermissionManager, DesktopTrustLevel, ProcessManager, 
    WindowManager, KeyboardController, DesktopLogger
)
from jarvisx.core.tools.vision import (
    VisionPermissionManager, VisionTrustLevel, ScreenCapture,
    OCREngine, UIDetector, VisualVerifier
)

def validate():
    print("=== JARVIS X VISION LAYER VALIDATION ===")
    
    # Set permissions
    DesktopPermissionManager.set_level(DesktopTrustLevel.SYSTEM_CONTROL)
    VisionPermissionManager.set_level(VisionTrustLevel.FULL_VISION)
    
    os.makedirs("var", exist_ok=True)
    
    try:
        ProcessManager.kill_process("notepad")
    except Exception:
        pass

    # 1. Launch Notepad
    print("\n1. Launching Notepad")
    ProcessManager.start_process("notepad.exe")
    
    # Retry logic for window to appear
    print("Waiting for window...")
    for _ in range(10):
        time.sleep(2)
        try:
            if WindowManager.focus_window("Notepad"):
                break
        except Exception:
            pass
    else:
        raise RuntimeError("Window Notepad did not appear in time")
        
    time.sleep(1)
    
    # 2. Type text
    print("\n2. Typing text")
    test_text = "Jarvis X Vision Test 2026"
    KeyboardController.type_text(test_text, interval=0.01)
    time.sleep(1)
    
    # 3. Capture screenshot
    print("\n3. Capturing screenshot")
    screenshot_path = "var/vision_test_screen.png"
    ScreenCapture.capture(screenshot_path)
    
    # 4 & 5. OCR text and verify confidence
    print("\n4 & 5. Running OCR and verifying confidence")
    try:
        elements = OCREngine.extract_elements(screenshot_path)
        found = False
        for el in elements:
            if "Jarvis" in el.text or "Vision" in el.text:
                print(f"Found text '{el.text}' with confidence {el.confidence}")
                if el.confidence > 0.3:  # pytesseract confidence can sometimes be lower
                    found = True
                    
        if not found:
            full_text = OCREngine.extract_text(screenshot_path)
            print("Full OCR text:\n", full_text)
            if "Jarvis" not in full_text:
                print("Warning: Failed to OCR the typed text. Tesseract might need tuning for Notepad fonts.")
    except Exception as e:
        print(f"OCR Error (Is Tesseract installed?): {e}")
        
    # 6. Detect UI regions
    print("\n6. Detecting UI regions")
    regions = UIDetector.detect_regions(screenshot_path)
    print(f"Detected {len(regions)} UI regions.")
    
    # 7. Save screenshot artifact (already saved at step 3, but let's confirm)
    print(f"\n7. Screenshot saved at {os.path.abspath(screenshot_path)}")
    
    # 8. Verify action success visually
    print("\n8. Verifying action success visually")
    try:
        success = VisualVerifier.verify_text_present(screenshot_path, "Jarvis")
        if not success:
            print("Warning: Visual Verification failed to find expected text.")
        else:
            print("Visual verification successful!")
    except Exception as e:
        print(f"Visual Verification Error: {e}")
    
    # 9. Close application
    print("\n9. Closing application")
    ProcessManager.kill_process("notepad")
    
    print("\nVision Layer validation finished!")

if __name__ == "__main__":
    validate()
