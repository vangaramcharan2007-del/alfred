from typing import List, Dict, Any, Optional
from .timeline import Timeline, Clip, AudioTrack, TitleOverlay, Transition, KenBurnsEffect

class TimelineBuilder:
    def __init__(self, fps: float = 30.0, resolution: tuple = (1920, 1080)):
        self.timeline = Timeline(fps=fps, resolution=resolution)
        
    def add_clip(self, filepath: str, media_type: str, duration: float, 
                 start_time: float = 0.0, ken_burns: Optional[KenBurnsEffect] = None,
                 color_grading: Optional[Dict] = None, speed_factor: float = 1.0) -> 'TimelineBuilder':
        
        clip = Clip(
            filepath=filepath,
            media_type=media_type,
            duration=duration,
            start_time=start_time,
            ken_burns=ken_burns,
            color_grading=color_grading or {},
            speed_factor=speed_factor
        )
        self.timeline.clips.append(clip)
        return self
        
    def add_transition(self, trans_type: str, duration: float, properties: Optional[Dict] = None) -> 'TimelineBuilder':
        if not self.timeline.clips:
            return self
            
        trans = Transition(type=trans_type, duration=duration, properties=properties or {})
        self.timeline.clips[-1].transition_out = trans
        return self
        
    def add_audio_track(self, filepath: str, volume: float = 1.0, fade_in: float = 0.0, fade_out: float = 0.0) -> 'TimelineBuilder':
        track = AudioTrack(filepath, volume, fade_in, fade_out)
        self.timeline.audio_tracks.append(track)
        return self
        
    def add_title(self, text: str, start_time: float, duration: float, style: str = "elegant") -> 'TimelineBuilder':
        title = TitleOverlay(text, start_time, duration, style)
        self.timeline.titles.append(title)
        return self
        
    def build(self) -> Timeline:
        return self.timeline
