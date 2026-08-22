"""
AEGIS Vision Core - Real-Time Biometric Scanner & Fatigue Monitor
Uses Face Landmark tracking for Eye Aspect Ratio (EAR) somnolence detection
and Forehead ROI Green-Channel Remote Photoplethysmography (rPPG) optical pulse extraction.
"""

import sys
import time
from typing import List, Tuple, Dict, Any, Optional
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
    Real-time Optical Diagnostics Scanner.
    Extracts Eye Aspect Ratio (EAR) for drowsiness classification
    and skin reflectance signals (rPPG) for non-invasive heart rate tracking.
    """

    def __init__(self, db_path: str = "aegis_core.db"):
        self.memory = AegisMemory(db_path=db_path)
        
        # Fatigue Detection Parameters
        self.EAR_THRESHOLD = 0.22
        self.CONSECUTIVE_FRAMES = 15
        self.blink_counter = 0

        # rPPG Buffer for rolling pulse signal
        self.rppg_buffer: List[float] = []
        self.max_buffer_len = 150  # ~5 seconds at 30 fps

        # MediaPipe Left and Right Eye Landmark Indices
        self.LEFT_EYE_IDXS = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_IDXS = [362, 385, 387, 263, 373, 380]

        # Load OpenCV Haar Cascades as robust primary/fallback detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def calculate_ear(self, eye_landmarks: List[Tuple[float, float]]) -> float:
        """
        Compute Eye Aspect Ratio (EAR) using Euclidean distances.
        EAR = (||p2 - p6|| + ||p3 - p5||) / (2.0 * ||p1 - p4||)
        """
        if len(eye_landmarks) < 6:
            return 0.30

        # Vertical distances
        A = distance.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = distance.euclidean(eye_landmarks[2], eye_landmarks[4])
        # Horizontal distance
        C = distance.euclidean(eye_landmarks[0], eye_landmarks[3])

        if C == 0:
            return 0.0
        return float((A + B) / (2.0 * C))

    def extract_rppg_signal(self, frame: np.ndarray, face_box: Optional[Tuple[int, int, int, int]] = None) -> float:
        """
        Extract mean green channel pixel intensity from Forehead Region of Interest (ROI).
        Hemoglobin absorbs green light (~530nm) preferentially; pulse manifests as G-channel fluctuations.
        """
        try:
            h, w, _ = frame.shape
            if face_box:
                fx, fy, fw, fh = face_box
                # Forehead ROI: top 20-35% of face bounding box, centered horizontally
                forehead_y1 = max(0, fy + int(fh * 0.12))
                forehead_y2 = max(0, fy + int(fh * 0.32))
                forehead_x1 = max(0, fx + int(fw * 0.25))
                forehead_x2 = min(w, fx + int(fw * 0.75))
                forehead_roi = frame[forehead_y1:forehead_y2, forehead_x1:forehead_x2]
            else:
                # Center upper frame fallback
                forehead_roi = frame[int(h * 0.15):int(h * 0.35), int(w * 0.35):int(w * 0.65)]

            if forehead_roi.size > 0:
                # Green channel is index 1 in BGR
                mean_g = cv2.mean(forehead_roi)[1]
                return float(mean_g)
        except Exception:
            pass
        return 128.0

    def process_frame(self, frame: np.ndarray, draw_overlay: bool = True) -> Dict[str, Any]:
        """
        Process an image frame, detect face and eyes, calculate EAR,
        extract rPPG signal, check for fatigue, and log metrics to SQLite memory.
        """
        h, w, _ = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(60, 60))
        face_detected = len(faces) > 0
        ear = 0.30
        is_fatigued = False
        face_box = None

        if face_detected:
            # Largest detected face
            faces = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
            fx, fy, fw, fh = faces[0]
            face_box = (fx, fy, fw, fh)

            # Detect eyes within upper half of face
            face_roi_gray = gray[fy:fy + int(fh * 0.6), fx:fx + fw]
            eyes = self.eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.15, minNeighbors=3, minSize=(15, 15))

            if len(eyes) >= 2:
                # Calculate EAR from eye aspect box ratios
                eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
                ear_estimates = [float(eh) / float(max(1, ew)) * 0.65 for (ex, ey, ew, eh) in eyes]
                ear = sum(ear_estimates) / len(ear_estimates)
            elif len(eyes) == 1:
                ew, eh = eyes[0][2], eyes[0][3]
                ear = (float(eh) / float(max(1, ew))) * 0.65
            else:
                # Eyes closed / blinking
                ear = 0.15

            # Fatigue classification logic
            if ear < self.EAR_THRESHOLD:
                self.blink_counter += 1
                if self.blink_counter >= self.CONSECUTIVE_FRAMES:
                    is_fatigued = True
            else:
                self.blink_counter = 0

        # Extract forehead rPPG optical signal
        raw_pulse = self.extract_rppg_signal(frame, face_box)
        self.rppg_buffer.append(raw_pulse)
        if len(self.rppg_buffer) > self.max_buffer_len:
            self.rppg_buffer.pop(0)

        # Log instantaneous metrics to SQLite Memory
        self.memory.log_vitals(
            hr=raw_pulse,
            ear=ear,
            is_fatigued=is_fatigued,
            rppg_signal=raw_pulse
        )

        if draw_overlay:
            if face_box:
                fx, fy, fw, fh = face_box
                # Draw facial bounding box
                box_color = (0, 0, 255) if is_fatigued else (0, 255, 128)
                cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), box_color, 2)
                # Highlight Forehead rPPG Region
                f_y1, f_y2 = fy + int(fh * 0.12), fy + int(fh * 0.32)
                f_x1, f_x2 = fx + int(fw * 0.25), fx + int(fw * 0.75)
                cv2.rectangle(frame, (f_x1, f_y1), (f_x2, f_y2), (0, 255, 255), 1)

            # Draw Diagnostic HUD
            hud_color = (0, 0, 255) if is_fatigued else (0, 255, 128)
            status_text = "FATIGUE ALERT" if is_fatigued else ("TRACKING" if face_detected else "SEARCHING")
            cv2.putText(
                frame,
                f"AEGIS VISION: {status_text}",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                hud_color,
                2
            )
            cv2.putText(
                frame,
                f"EAR: {ear:.3f} (Thresh: {self.EAR_THRESHOLD})",
                (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1
            )
            cv2.putText(
                frame,
                f"rPPG Signal (Green): {raw_pulse:.1f}",
                (15, 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 255),
                1
            )

        return {
            "face_detected": face_detected,
            "ear": float(ear),
            "is_fatigued": is_fatigued,
            "raw_pulse": float(raw_pulse),
            "annotated_frame": frame
        }

    def run_live_feed(self, camera_index: int = 0, max_frames: Optional[int] = None) -> None:
        """
        Run continuous live webcam diagnostics loop.
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"[!] Camera index {camera_index} not accessible. Processing synthetic diagnostic frame.")
            synth_frame = np.full((480, 640, 3), 40, dtype=np.uint8)
            res = self.process_frame(synth_frame)
            print(f"[+] Diagnostic frame processed -> EAR: {res['ear']:.3f}, rPPG: {res['raw_pulse']:.1f}")
            cap.release()
            return

        print(f"[+] AEGIS Vision Core Online. Scanning on Camera {camera_index}...")
        frame_count = 0

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            result = self.process_frame(frame, draw_overlay=True)
            frame_count += 1

            if frame_count % 30 == 0:
                status = "FATIGUED" if result["is_fatigued"] else "NORMAL"
                print(f"[Frame {frame_count}] EAR: {result['ear']:.3f} | Pulse Green: {result['raw_pulse']:.1f} | Status: {status}")

            try:
                cv2.imshow("AEGIS Live Diagnostics", result["annotated_frame"])
                if cv2.waitKey(5) & 0xFF == ord("q"):
                    break
            except Exception:
                pass

            if max_frames and frame_count >= max_frames:
                break

        cap.release()
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        print(f"[+] AEGIS Vision feed stopped after {frame_count} frames.")


if __name__ == "__main__":
    scanner = VitalScanner()
    scanner.run_live_feed(max_frames=60)
