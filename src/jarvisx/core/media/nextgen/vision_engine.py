import os
import cv2
import numpy as np
from pathlib import Path
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format='[Alfred Vision] %(message)s')

class VisionEngine:
    def __init__(self, assets_dir=r"C:\Users\vanga\Desktop\Project_Tirupati\Assets"):
        self.assets_dir = Path(assets_dir)
        self.model_dir = self.assets_dir / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # We will use MobileNet SSD for quick object detection (people, etc.)
        # and standard MobileNetV2 classification for scene context (temple, landscape).
        # For simplicity and robust URL availability, we'll download MobileNet SSD from official OpenCV repo.
        self.proto_file = self.model_dir / "MobileNetSSD_deploy.prototxt"
        self.weights_file = self.model_dir / "MobileNetSSD_deploy.caffemodel"
        
        self.classes = ["background", "aeroplane", "bicycle", "bird", "boat",
                        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                        "sofa", "train", "tvmonitor"]
        
        self._ensure_models()
        self.net = cv2.dnn.readNetFromCaffe(str(self.proto_file), str(self.weights_file))

    def _ensure_models(self):
        proto_url = "https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/voc/MobileNetSSD_deploy.prototxt"
        weights_url = "https://media.githubusercontent.com/media/chuanqi305/MobileNet-SSD/master/voc/MobileNetSSD_deploy.caffemodel"
        
        if not self.proto_file.exists():
            logging.info("Downloading MobileNet SSD Prototxt...")
            urllib.request.urlretrieve(proto_url, str(self.proto_file))
            
        if not self.weights_file.exists():
            logging.info("Downloading MobileNet SSD Weights (~22MB)...")
            urllib.request.urlretrieve(weights_url, str(self.weights_file))
            
    def _detect_blur(self, gray_img):
        return cv2.Laplacian(gray_img, cv2.CV_64F).var()

    def _detect_lighting(self, gray_img):
        return np.mean(gray_img)
        
    def _detect_objects(self, img):
        (h, w) = img.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        found = []
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.4:
                idx = int(detections[0, 0, i, 1])
                found.append(self.classes[idx])
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
        # and based on image complexity/edges.
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (img.shape[0] * img.shape[1])
        
        scene_type = "landscape"
        if "person" in objects:
            scene_type = "people"
        if edge_density > 25.0: # Highly complex structure -> Temple/Architecture heuristic
            scene_type = "temple"
            
        scenic_score = 0
        if 80 < light < 200: scenic_score += 3 # Good lighting
        if blur > 100: scenic_score += 4 # Sharp image
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
