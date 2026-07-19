import cv2
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[Alfred Vision] %(message)s')

class VisionEngine:
    def __init__(self, assets_dir=r"C:\Users\vanga\Desktop\Project_Tirupati\Assets"):
        self.assets_dir = Path(assets_dir)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def _detect_blur(self, gray_img):
        return cv2.Laplacian(gray_img, cv2.CV_64F).var()

    def _detect_lighting(self, gray_img):
        return np.mean(gray_img)
        
    def _detect_objects(self, img):
        # Use built-in OpenCV HOG descriptor for robust local person detection without downloading external models
        found = []
        # Resize for faster HOG detection
        h, w = img.shape[:2]
        if w > 800:
            scale = 800 / float(w)
            img = cv2.resize(img, (800, int(h * scale)))
            
        boxes, weights = self.hog.detectMultiScale(img, winStride=(8, 8), padding=(4, 4), scale=1.05)
        if len(boxes) > 0:
            found.append("person")
            
        return found

    def analyze_media(self, filepath: str):
        """Analyzes a photo or the first frame of a video."""
        path = Path(filepath)
        is_video = path.suffix.lower() in ['.mp4', '.mov', '.avi']
        
        if is_video:
            cap = cv2.VideoCapture(str(filepath))
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return None
            img = frame
        else:
            img = cv2.imread(str(filepath))
            
        if img is None:
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        blur = self._detect_blur(gray)
        light = self._detect_lighting(gray)
        objects = self._detect_objects(img)
        
        # Simple heuristics for "Landscape" or "Temple" if person is not the dominating object
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (img.shape[0] * img.shape[1])
        
        scene_type = "landscape"
        if "person" in objects:
            scene_type = "people"
        if edge_density > 25.0:
            scene_type = "temple"
            
        scenic_score = 0
        if 80 < light < 200: scenic_score += 3
        if blur > 100: scenic_score += 4
        if scene_type == "landscape": scenic_score += 2
        
        return {
            'filepath': str(filepath),
            'type': 'video' if is_video else 'photo',
            'blur_score': float(blur),
            'lighting_score': float(light),
            'objects': list(set(objects)),
            'scene_type': scene_type,
            'scenic_score': float(scenic_score)
        }
