from typing import List, Dict, Any
from .timeline_builder import TimelineBuilder
from .timeline import Timeline, KenBurnsEffect
import logging
import random

logging.basicConfig(level=logging.INFO, format='[Alfred Story] %(message)s')

class StoryEngine:
    def __init__(self, fps=30.0, resolution=(1920, 1080)):
        self.fps = fps
        self.resolution = resolution
        
    def _categorize_clips(self, analysis_results: List[Dict]) -> Dict[str, List[Dict]]:
        # Sort all by scenic score descending
        sorted_clips = sorted(analysis_results, key=lambda x: x.get('scenic_score', 0), reverse=True)
        
        categories = {
            'landscapes': [c for c in sorted_clips if c['scene_type'] == 'landscape'],
            'temples': [c for c in sorted_clips if c['scene_type'] == 'temple'],
            'people': [c for c in sorted_clips if c['scene_type'] == 'people'],
            'all': sorted_clips
        }
        return categories

    def build_narrative(self, analysis_results: List[Dict], music_path: str, beat_markers: list) -> Timeline:
        """
        Translates raw media and music beats into a structured Universal Timeline.
        Narrative Arc: Hook -> Build-up -> Journey -> Emotional Peak -> Ending
        """
        logging.info("Constructing narrative arc...")
        builder = TimelineBuilder(fps=self.fps, resolution=self.resolution)
        builder.add_audio_track(music_path, volume=1.0, fade_in=2.0, fade_out=3.0)
        
        cats = self._categorize_clips(analysis_results)
        
        if not cats['all']:
            logging.error("No valid media to build story!")
            return builder.build()
            
        # 1. The Hook (Highest scenic score, preferably a landscape or temple)
        hook_pool = cats['landscapes'] + cats['temples']
        hook = hook_pool[0] if hook_pool else cats['all'][0]
        
        # 2. Emotional Peak (Highest score people/temple)
        peak_pool = cats['people'] + cats['temples']
        peak = peak_pool[0] if peak_pool else cats['all'][1 % len(cats['all'])]
        
        # 3. Ending (Stable landscape)
        end = cats['landscapes'][-1] if cats['landscapes'] else cats['all'][-1]
        
        # 4. Fill the Journey (everything else)
        used_paths = {hook['filepath'], peak['filepath'], end['filepath']}
        journey = [c for c in cats['all'] if c['filepath'] not in used_paths]
        
        # Assemble the Arc sequence
        story_sequence = [hook] + journey[:len(journey)//2] + [peak] + journey[len(journey)//2:] + [end]
        
        # Synchronize to beats
        # Filter strong beats
        strong_beats = [b for b in beat_markers if b.strength > np.percentile([m.strength for m in beat_markers], 70)] if beat_markers else []
        
        current_time = 0.0
        
        builder.add_title("TIRUPATI", start_time=0.5, duration=3.0, style="cinematic")
        
        for i, clip in enumerate(story_sequence):
            # Calculate duration based on the next strong beat, or fallback to 3 seconds
            duration = 3.0
            if strong_beats:
                # Find the next beat after current_time + minimum clip duration (1.5s)
                next_beats = [b.time for b in strong_beats if b.time > current_time + 1.5]
                if next_beats:
                    duration = min(next_beats[0] - current_time, 4.0) # Cap at 4s
            
            # Apply dynamic Ken Burns if it's a photo
            kb = None
            if clip['type'] == 'photo':
                kb = KenBurnsEffect(
                    start_scale=1.1, end_scale=1.3,
                    start_x=0.5, start_y=0.5,
                    end_x=0.5 + random.uniform(-0.1, 0.1), 
                    end_y=0.5 + random.uniform(-0.1, 0.1)
                )
                
            # Add to builder
            builder.add_clip(
                filepath=clip['filepath'],
                media_type=clip['type'],
                duration=duration,
                start_time=0.0,
                ken_burns=kb,
                color_grading={'brightness': 1.05, 'contrast': 1.1} # Slight cinematic punch
            )
            
            # Add transitions (except for the last clip)
            if i < len(story_sequence) - 1:
                # If it aligned with a strong beat, use a hard cut or flash, else crossfade
                trans_type = "crossfade" if duration >= 3.0 else "luma"
                builder.add_transition(trans_type, duration=0.5)
                
            current_time += duration
            
        logging.info(f"Story built successfully with {len(story_sequence)} clips synced to music.")
        return builder.build()

import numpy as np # required for percentile
