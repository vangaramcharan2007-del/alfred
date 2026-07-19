import os
import glob
import time
import logging
from pathlib import Path

from .collector import Collector
from .vision_engine import VisionEngine
from .music_engine import MusicEngine
from .story_engine import StoryEngine
from .renderer_shotcut import ShotcutAdapter
from .verifier import Verifier
from .showcase import Showcase

logging.basicConfig(level=logging.INFO, format='[Alfred Director] %(message)s')

class NextGenOrchestrator:
    def __init__(self):
        self.workspace = Path(r"C:\Users\vanga\Desktop\Project_Tirupati")
        
    def run(self):
        logging.info("Initiating Next-Gen AI Creative Director...")
        
        # Phase 1: Collect
        collector = Collector()
        collector.run()
        
        # Phase 2 & 3: Vision Engine
        vision = VisionEngine()
        raw_files = glob.glob(str(self.workspace / "Originals" / "*.*"))
        
        analysis_results = []
        for f in raw_files:
            logging.info(f"Analyzing {Path(f).name}...")
            res = vision.analyze_media(f)
            if res:
                analysis_results.append(res)
                
        # Phase 4: Music Engine
        music = MusicEngine()
        audio_path, beat_markers = music.analyze_beats()
        
        # Phase 5: Story Engine
        story = StoryEngine()
        timeline = story.build_narrative(analysis_results, audio_path, beat_markers)
        timeline.beat_markers = beat_markers # Save for showcase
        
        # Phase 6: Render
        renderer = ShotcutAdapter()
        output_mp4 = str(self.workspace / "Exports" / "Tirupati_Cinematic_Film.mp4")
        
        start_time = time.time()
        success = renderer.render(timeline, output_mp4, str(self.workspace / "Timeline"))
        render_duration = time.time() - start_time
        
        # Phase 7: Verifier
        verifier = Verifier()
        if success and verifier.check_quality(output_mp4):
            # Phase 8: Showcase
            showcase = Showcase()
            showcase.display_stats(timeline, len(raw_files), render_duration)
            showcase.auto_play(output_mp4)
        else:
            logging.error("Final product failed quality verification. Re-render required.")
            
if __name__ == "__main__":
    director = NextGenOrchestrator()
    director.run()
