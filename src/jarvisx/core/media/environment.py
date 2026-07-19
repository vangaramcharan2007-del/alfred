import os
import sys
import shutil

class EnvironmentManager:
    @staticmethod
    def ensure_directories(base_path):
        dirs = ["Photos", "Videos", "Audio", "Assets", "Cache", "Project", "Exports"]
        os.makedirs(base_path, exist_ok=True)
        for d in dirs:
            os.makedirs(os.path.join(base_path, d), exist_ok=True)
            
    @staticmethod
    def verify_ffmpeg():
        """Ensure FFmpeg is available for MoviePy."""
        # moviepy handles its own imageio_ffmpeg binaries, but we can verify
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_exe
            return True
        except ImportError:
            print("[Warning] imageio_ffmpeg not found. MoviePy may fail.")
            return False
