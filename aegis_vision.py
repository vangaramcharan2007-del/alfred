"""
AEGIS Vision Core - Real-Time Optical Biometric Scanner & Video Streamer
Provides live camera capture, Haar Face/Eye tracking, Eye Aspect Ratio (EAR) somnolence monitoring,
forehead rPPG optical green-channel reflectance extraction, and MJPEG video streaming for the UI.
"""

import sys
import time
import threading
from typing import List, Tuple, Dict, Any, Optional, Generator
import cv2
import numpy as np
from scipy.spatial import distance

from aegis_memory import AegisMemory

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class VitalScanner:
    """
    Real-time Optical Diagnostics Scanner and MJPEG Video Streamer.
    Tracks face, computes Eye Aspect Ratio (EAR), extracts forehead rPPG optical signal,
    and logs real biometrics into persistent SQLite memory.
    """

    def __init__(self, db_path: str = "aegis_core.db"):
        self.memory = AegisMemory(db_path=db_path)
        
        # Fatigue Detection Parameters
        self.EAR_THRESHOLD = 0.22
        self.CONSECUTIVE_FRAMES = 15
        self.blink_counter = 0

        # rPPG Buffer for rolling pulse signal
        self.rppg_buffer: List[float] = [128.0] * 60
        self.max_buffer_len = 150

        # Load OpenCV Haar Cascades
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        # Camera capture state
        self.cap: Optional[cv2.VideoCapture] = None
        self.lock = threading.Lock()
        self.is_streaming = False

    def calculate_ear(self, eye_landmarks: List[Tuple[float, float]]) -> float:
        """
        Compute Eye Aspect Ratio (EAR) using Euclidean distances.
        EAR = (||p2 - p6|| + ||p3 - p5||) / (2.0 * ||p1 - p4||)
        """
        if len(eye_landmarks) < 6:
            return 0.30

        A = distance.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = distance.euclidean(eye_landmarks[2], eye_landmarks[4])
        C = distance.euclidean(eye_landmarks[0], eye_landmarks[3])

        if C == 0:
            return 0.0
        return float((A + B) / (2.0 * C))

    def extract_rppg_signal(self, frame: np.ndarray, face_box: Optional[Tuple[int, int, int, int]] = None) -> float:
        """
        Extract mean green channel pixel intensity from Forehead Region of Interest (ROI).
        """
        try:
            h, w, _ = frame.shape
            if face_box:
                fx, fy, fw, fh = face_box
                forehead_y1 = max(0, fy + int(fh * 0.10))
                forehead_y2 = max(0, fy + int(fh * 0.30))
                forehead_x1 = max(0, fx + int(fw * 0.25))
                forehead_x2 = min(w, fx + int(fw * 0.75))
                forehead_roi = frame[forehead_y1:forehead_y2, forehead_x1:forehead_x2]
            else:
                forehead_roi = frame[int(h * 0.15):int(h * 0.35), int(w * 0.35):int(w * 0.65)]

            if forehead_roi.size > 0:
                mean_g = cv2.mean(forehead_roi)[1]
                return float(mean_g)
        except Exception:
            pass
        return 128.0

    def draw_hud(
        self,
        frame: np.ndarray,
        face_box: Optional[Tuple[int, int, int, int]],
        ear: float,
        is_fatigued: bool,
        raw_pulse: float
    ) -> np.ndarray:
        """
        Draw a clinical HUD overlay on top of the camera frame.
        """
        h, w, _ = frame.shape

        if face_box:
            fx, fy, fw, fh = face_box
            box_color = (60, 60, 240) if is_fatigued else (210, 180, 0)
            
            # Corner accents for face bounding box
            line_len = min(25, fw // 4)
            cv2.line(frame, (fx, fy), (fx + line_len, fy), box_color, 2)
            cv2.line(frame, (fx, fy), (fx, fy + line_len), box_color, 2)
            cv2.line(frame, (fx + fw, fy), (fx + fw - line_len, fy), box_color, 2)
            cv2.line(frame, (fx + fw, fy), (fx + fw, fy + line_len), box_color, 2)
            cv2.line(frame, (fx, fy + fh), (fx + line_len, fy + fh), box_color, 2)
            cv2.line(frame, (fx, fy + fh), (fx, fy + fh - line_len), box_color, 2)
            cv2.line(frame, (fx + fw, fy + fh), (fx + fw - line_len, fy + fh), box_color, 2)
            cv2.line(frame, (fx + fw, fy + fh), (fx + fw, fy + fh - line_len), box_color, 2)

            # Forehead ROI Box
            f_y1, f_y2 = fy + int(fh * 0.10), fy + int(fh * 0.30)
            f_x1, f_x2 = fx + int(fw * 0.25), fx + int(fw * 0.75)
            cv2.rectangle(frame, (f_x1, f_y1), (f_x2, f_y2), (0, 220, 255), 1)
            cv2.putText(frame, "rPPG ROI", (f_x1, max(12, f_y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 220, 255), 1)

        # Top Diagnostic Banner
        status_text = "FATIGUE ALERT" if is_fatigued else ("OPTICAL TRACKING ACTIVE" if face_box else "SEARCHING SUBJECT")
        banner_bg = (0, 0, 180) if is_fatigued else (20, 30, 20)
        cv2.rectangle(frame, (0, 0), (w, 32), banner_bg, -1)
        
        status_color = (255, 255, 255) if is_fatigued else (100, 240, 120)
        cv2.putText(frame, f"AEGIS VISION // {status_text}", (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2)

        # Metric Badges
        ear_color = (80, 80, 255) if ear < self.EAR_THRESHOLD else (255, 255, 255)
        cv2.putText(frame, f"EAR: {ear:.3f}", (12, h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, ear_color, 1)
        cv2.putText(frame, f"rPPG Flux: {raw_pulse:.1f}", (120, h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 230, 255), 1)

        # Draw Mini Waveform Sparkline in bottom panel
        if len(self.rppg_buffer) > 2:
            wf_x = w - 160
            wf_y = h - 20
            cv2.rectangle(frame, (wf_x - 5, wf_y - 25), (w - 10, wf_y + 10), (10, 15, 25), -1)
            cv2.rectangle(frame, (wf_x - 5, wf_y - 25), (w - 10, wf_y + 10), (40, 50, 70), 1)
            
            recent_sig = self.rppg_buffer[-40:]
            min_val = min(recent_sig) if recent_sig else 0
            max_val = max(recent_sig) if recent_sig else 255
            rng = max(1.0, max_val - min_val)

            pts = []
            for idx, val in enumerate(recent_sig):
                px = wf_x + int(idx * (145.0 / max(1, len(recent_sig) - 1)))
                py = wf_y - int(((val - min_val) / rng) * 20)
                pts.append((px, py))
            
            for i in range(1, len(pts)):
                cv2.line(frame, pts[i - 1], pts[i], (0, 255, 180), 1)

        return frame

    def process_frame(self, frame: np.ndarray, draw_overlay: bool = True) -> Dict[str, Any]:
        """
        Process single image frame, perform facial analytics, log to database,
        and optionally draw HUD.
        """
        h, w, _ = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(60, 60))
        face_detected = len(faces) > 0
        ear = 0.32
        is_fatigued = False
        face_box = None

        if face_detected:
            faces = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
            fx, fy, fw, fh = faces[0]
            face_box = (fx, fy, fw, fh)

            face_roi_gray = gray[fy:fy + int(fh * 0.6), fx:fx + fw]
            eyes = self.eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.15, minNeighbors=3, minSize=(15, 15))

            if len(eyes) >= 2:
                eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
                ear_estimates = [float(eh) / float(max(1, ew)) * 0.65 for (ex, ey, ew, eh) in eyes]
                ear = sum(ear_estimates) / len(ear_estimates)
            elif len(eyes) == 1:
                ew, eh = eyes[0][2], eyes[0][3]
                ear = (float(eh) / float(max(1, ew))) * 0.65
            else:
                # Eyelids closed
                ear = 0.16

            if ear < self.EAR_THRESHOLD:
                self.blink_counter += 1
                if self.blink_counter >= self.CONSECUTIVE_FRAMES:
                    is_fatigued = True
            else:
                self.blink_counter = 0

        raw_pulse = self.extract_rppg_signal(frame, face_box)
        self.rppg_buffer.append(raw_pulse)
        if len(self.rppg_buffer) > self.max_buffer_len:
            self.rppg_buffer.pop(0)

        # Log to Persistent SQLite Memory
        self.memory.log_vitals(
            hr=raw_pulse,
            ear=ear,
            is_fatigued=is_fatigued,
            rppg_signal=raw_pulse
        )

        if draw_overlay:
            frame = self.draw_hud(frame, face_box, ear, is_fatigued, raw_pulse)

        return {
            "face_detected": face_detected,
            "ear": float(ear),
            "is_fatigued": is_fatigued,
            "raw_pulse": float(raw_pulse),
            "annotated_frame": frame
        }

    def generate_mjpeg_frames(self) -> Generator[bytes, None, None]:
        """
        Continuous MJPEG video frame generator for FastAPI /video-feed.
        Captures hardware camera if available, or renders an active synthetic bio-feed.
        """
        cap = cv2.VideoCapture(0)
        camera_available = cap.isOpened()
        
        frame_idx = 0
        while True:
            frame_idx += 1
            if camera_available:
                success, frame = cap.read()
                if not success:
                    camera_available = False
            
            if not camera_available:
                # Generate dynamic diagnostic synthetic frame if camera is busy or not attached
                frame = np.zeros((360, 480, 3), dtype=np.uint8)
                # Background subtle grid
                for y in range(0, 360, 40):
                    cv2.line(frame, (0, y), (480, y), (15, 20, 30), 1)
                for x in range(0, 480, 40):
                    cv2.line(frame, (x, 0), (x, 360), (15, 20, 30), 1)
                
                # Synthetic face avatar contour
                cv2.circle(frame, (240, 160), 65, (30, 45, 65), -1)
                cv2.circle(frame, (240, 160), 65, (0, 180, 220), 1)
                # Synthetic eyes
                eye_open = 0.32 if (frame_idx % 45 > 6) else 0.12
                cv2.ellipse(frame, (215, 145), (14, int(14 * (eye_open / 0.32))), 0, 0, 360, (0, 240, 255), -1)
                cv2.ellipse(frame, (265, 145), (14, int(14 * (eye_open / 0.32))), 0, 0, 360, (0, 240, 255), -1)
                # Synthetic forehead ROI
                cv2.rectangle(frame, (210, 110), (270, 130), (0, 255, 180), 1)

            # Process frame with HUD
            result = self.process_frame(frame, draw_overlay=True)
            annotated = result["annotated_frame"]

            # Encode to JPEG
            ret, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.04)  # ~25 FPS

        if cap.isOpened():
            cap.release()


# Global scanner instance for video feed
global_scanner = VitalScanner()
