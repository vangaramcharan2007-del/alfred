import os
import time
import glob
from PIL import ImageGrab
import cv2

DEST_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "Project_Tirupati", "Exports")
ARTIFACTS_DIR = r"C:\Users\vanga\.gemini\antigravity\brain\7f0afe60-98ed-468b-a13e-245c8289f22f"

def capture_screenshot(name):
    try:
        img = ImageGrab.grab()
        path = os.path.join(ARTIFACTS_DIR, f"{name}.jpg")
        img.save(path)
        return path
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return None

def verify():
    print("Waiting for video render to complete...")
    video_path = os.path.join(DEST_DIR, "Tirupati_Cinematic_Film.mp4")
    
    # Wait up to 5 minutes for the render to finish
    for _ in range(60):
        if os.path.exists(video_path):
            break
        time.sleep(5)
        
    if not os.path.exists(video_path):
        print("Video render timed out or failed.")
        return

    # Give it a few seconds to finalize the file write
    time.sleep(5)
    
    print("\n--- Deliverables ---")
    files = glob.glob(os.path.join(DEST_DIR, "*.*"))
    for f in files:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"Path: {f} | Size: {size_mb:.2f} MB")
        
        if f.endswith('.mp4'):
            cap = cv2.VideoCapture(f)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if fps > 0:
                duration = frame_count / fps
                print(f"  -> Video Duration: {duration:.2f} seconds")
            cap.release()

    # Capture screenshots of the environment
    print("\nTaking screenshot of the Exports folder...")
    os.startfile(DEST_DIR)
    time.sleep(3)
    folder_ss = capture_screenshot("screenshot_exports_folder")
    if folder_ss: print(f"Screenshot saved to {folder_ss}")
    
    print("\nTaking screenshot of the Video Playback...")
    os.startfile(video_path)
    time.sleep(4)
    # Attempt fullscreen via F11
    import pywinauto
    try:
        pywinauto.keyboard.send_keys('{F11}')
    except:
        pass
    time.sleep(2)
    play_ss = capture_screenshot("screenshot_video_playback")
    if play_ss: print(f"Screenshot saved to {play_ss}")
    
    print("\nVerification Complete.")

if __name__ == "__main__":
    verify()
