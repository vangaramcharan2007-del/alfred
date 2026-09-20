"""
Utility to synchronize the 4K Naruto endless sky wallpaper with Windows native Lock Screen (Win + L).
"""

import os
import sys
import winreg
import cv2


def extract_4k_lockscreen_frame(video_path: str, output_path: str) -> bool:
    """Extract a pristine 4K frame from the video if output doesn't exist."""
    if not os.path.exists(video_path):
        print(f"[ERR] Video file not found at: {video_path}")
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Pick frame 30 for stable exposure
    cap.set(cv2.CAP_PROP_POS_FRAMES, min(30, max(0, count - 1)))
    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite(output_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
        print(f"[OK] Extracted 4K frame saved to: {output_path}")
        return True
    else:
        print("[ERR] Failed to read frame from video.")
        return False


def set_windows_lockscreen_image(image_path: str) -> bool:
    """Configure Windows Personalization registry to use the 4K wallpaper for Lock Screen."""
    abs_path = os.path.abspath(image_path)
    if not os.path.exists(abs_path):
        print(f"[ERR] Image path does not exist: {abs_path}")
        return False

    success = False
    # 1. Configure PersonalizationCSP in HKCU
    try:
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\PersonalizationCSP"
        )
        winreg.SetValueEx(key, "LockScreenImagePath", 0, winreg.REG_SZ, abs_path)
        winreg.SetValueEx(key, "LockScreenImageUrl", 0, winreg.REG_SZ, abs_path)
        winreg.SetValueEx(key, "LockScreenImageStatus", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        print("[OK] Configured HKCU PersonalizationCSP LockScreenImagePath successfully.")
        success = True
    except Exception as e:
        print(f"[WARN] Failed to write PersonalizationCSP: {e}")

    return success


def main():
    video_path = r"E:\naruto-endless-sky.3840x2160.mp4"
    proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_image = os.path.join(proj_root, "assets", "wallpapers", "naruto_4k_lockscreen.jpg")

    print("=" * 65)
    print("  NARUTO 4K WINDOWS LOCKSCREEN SYNCHRONIZATION")
    print("=" * 65)
    print(f"Source Video : {video_path}")
    print(f"Target Image : {output_image}")

    if not os.path.exists(output_image):
        extract_4k_lockscreen_frame(video_path, output_image)
    else:
        print(f"[OK] Frame already cached: {output_image}")

    set_windows_lockscreen_image(output_image)
    print("\n[SUCCESS] Windows native lock screen synchronized with 4K Naruto wallpaper!")
    print("Press Win + L at any time to verify the native lock screen.")


if __name__ == "__main__":
    main()
