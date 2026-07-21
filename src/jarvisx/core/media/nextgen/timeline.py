from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class KenBurnsEffect:
    start_scale: float
    end_scale: float
    duration: float

@dataclass
class KenBurnsEffect:
    start_scale: float
    end_scale: float
    duration: float
    start_x: float = 0.5
    start_y: float = 0.5
    end_x: float = 0.5
    end_y: float = 0.5

@dataclass
class Transition:
    type: str = "crossfade"
    duration: float = 0.5
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Clip:
    filepath: str
    media_type: str # 'photo' or 'video'
    duration: float
    start_time: float = 0.0 # for trimming videos
    ken_burns: Optional[KenBurnsEffect] = None
    transition_in: Optional[Transition] = None
    transition_out: Optional[Transition] = None
    color_grading: Dict[str, float] = field(default_factory=dict) # e.g. {'brightness': 1.1, 'contrast': 1.2, 'saturation': 1.1}
    speed_factor: float = 1.0

@dataclass
class AudioTrack:
    filepath: str
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0

@dataclass
class TitleOverlay:
    text: str
    start_time: float
    duration: float
    style: str = "elegant"
    animation: str = "fade"

@dataclass
class BeatMarker:
    time: float
    strength: float

@dataclass
class Timeline:
    clips: List[Clip] = field(default_factory=list)
    audio_tracks: List[AudioTrack] = field(default_factory=list)
    transitions: List[Transition] = field(default_factory=list)
    titles: List[TitleOverlay] = field(default_factory=list)
    beat_markers: List[BeatMarker] = field(default_factory=list)
    resolution: tuple = (1920, 1080)
    fps: float = 30.0
