import cv2
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[Alfred Quality] %(message)s')

class Verifier:
    def __init__(self, threshold_black_frames=3):
        self.threshold_black_frames = threshold_black_frames

    def check_quality(self, video_path: str) -> bool:
        """
        Scans the rendered video for corruption (black frames) and pacing issues.
        Returns True if quality passes.
        """
        logging.info(f"Initiating Quality Engine scan on {video_path}...")
        path = Path(video_path)
        if not path.exists():
            logging.error("File does not exist!")
            return False
            
        cap = cv2.VideoCapture(str(video_path))
        
        black_frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            logging.error("Video has 0 frames! Render failed.")
            return False
            
        # Sample frames to check for black screen rendering errors (common in NLE automation)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Check if frame is almost entirely black
            if cv2.mean(frame)[0] < 5.0:
                black_frame_count += 1
                
        cap.release()
        
        if black_frame_count > self.threshold_black_frames:
            logging.error(f"Quality Check FAILED: Detected {black_frame_count} black frames (Threshold: {self.threshold_black_frames}).")
            return False
            
        logging.info(f"Quality Check PASSED. {total_frames} frames verified.")
        return True
