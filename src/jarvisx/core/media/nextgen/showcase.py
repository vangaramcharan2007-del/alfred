import os
import logging
from pathlib import Path
import time
from .timeline import Timeline

logging.basicConfig(level=logging.INFO, format='[Alfred Showcase] %(message)s')

class Showcase:
    def __init__(self):
        pass
        
    def display_stats(self, timeline: Timeline, total_files: int, render_time: float):
        print("\n" + "="*50)
        print(" AI CREATIVE DIRECTOR: PROJECT TIRUPATI ")
        print("="*50)
        print(f"• Total Raw Media Analyzed: {total_files}")
        print(f"• Clips Selected for Edit:  {len(timeline.clips)}")
        print(f"• Clips Rejected by AI:     {total_files - len(timeline.clips)}")
        print(f"• Audio Beat Markers Synced:{len(timeline.beat_markers)}")
        print(f"• Render Engine Used:       Shotcut MLT XML")
        print(f"• Render Time:              {render_time:.2f} seconds")
        print("="*50)
        print("STORY ARC STRUCTURE:")
        if timeline.clips:
            print(f"  [Hook]     {Path(timeline.clips[0].filepath).name}")
            print(f"  [Journey]  {len(timeline.clips)-2} clips transitioning on beat")
            print(f"  [Ending]   {Path(timeline.clips[-1].filepath).name}")
        print("="*50)
        
    def auto_play(self, video_path: str):
        logging.info(f"Initiating Grand Finale playback: {video_path}")
        if os.path.exists(video_path):
            os.startfile(video_path)
            # Try to push to fullscreen
            time.sleep(3)
            try:
                import pywinauto
                pywinauto.keyboard.send_keys('{F11}')
            except:
                pass
        else:
            logging.error(f"Cannot play {video_path}: File not found.")
