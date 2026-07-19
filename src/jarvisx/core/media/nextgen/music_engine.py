import librosa
import numpy as np
import logging
import urllib.request
from pathlib import Path
from .timeline import BeatMarker

logging.basicConfig(level=logging.INFO, format='[Alfred Music] %(message)s')

class MusicEngine:
    def __init__(self, assets_dir=r"C:\Users\vanga\Desktop\Project_Tirupati\Assets"):
        self.assets_dir = Path(assets_dir)
        self.audio_dir = self.assets_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.default_track = self.audio_dir / "cinematic_travel.mp3"
        
    def _ensure_track(self):
        # A lightweight royalty-free cinematic track for demonstration (Pixabay or similar free host)
        # Using a reliable fallback URL for demonstration purposes.
        url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        if not self.default_track.exists():
            logging.info("Downloading royalty-free cinematic track...")
            urllib.request.urlretrieve(url, str(self.default_track))
        return str(self.default_track)

    def analyze_beats(self, filepath=None) -> tuple[str, list[BeatMarker]]:
        """
        Loads the audio, calculates BPM, and detects strong beat onsets to drive video transitions.
        """
        track_path = filepath if filepath else self._ensure_track()
        logging.info(f"Analyzing audio beats for {track_path}...")
        
        y, sr = librosa.load(track_path)
        
        # Get tempo and beats
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        
        # Convert frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        # Compute onset strength to rank the 'epicness' of each beat
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        markers = []
        for i, t in enumerate(beat_times):
            frame = beat_frames[i]
            # Strength is local max of onset envelope around the beat
            local_strength = np.max(onset_env[max(0, frame-5):min(len(onset_env), frame+5)])
            markers.append(BeatMarker(time=float(t), strength=float(local_strength)))
            
        logging.info(f"Detected {len(markers)} beat markers at {tempo[0]:.0f} BPM.")
        return track_path, markers
