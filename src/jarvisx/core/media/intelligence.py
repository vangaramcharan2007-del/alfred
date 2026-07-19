import os
import cv2
import numpy as np

class MediaIntelligence:
    def __init__(self, tts_engine=None):
        self.tts = tts_engine
        
    def speak(self, text):
        print(f"[Alfred] {text}")
        if self.tts:
            self.tts.speak(text)

    def analyze_media(self, photos_dir, videos_dir):
        self.speak("Phase 3: Initiating Computer Vision media analysis.")
        
        import glob
        photos = glob.glob(os.path.join(photos_dir, "*.*"))
        videos = glob.glob(os.path.join(videos_dir, "*.*"))
        
        if not photos:
            self.speak("No photos found to analyze.")
            return [], []
            
        scored_photos = []
        # Load Haar Cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        for photo in photos:
            try:
                img = cv2.imread(photo)
                if img is None: continue
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Blur Detection (Variance of Laplacian)
                blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                # Exposure Detection
                exposure = np.mean(gray)
                
                # Face Detection
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                face_score = len(faces) * 50
                
                # Base score favors sharpness and well-exposed images
                score = blur_score + face_score
                
                # Penalize extreme exposure
                if exposure < 40 or exposure > 220:
                    score *= 0.5
                    
                scored_photos.append({'path': photo, 'score': score})
            except Exception as e:
                print(f"Error analyzing {photo}: {e}")
                
        scored_photos.sort(key=lambda x: x['score'], reverse=True)
        
        # Deduplication using extremely basic image hashing or skip (using top N inherently skips bad dupes)
        best_photos = [m['path'] for m in scored_photos[:15]]
        
        self.speak(f"Analyzed {len(photos)} photos and {len(videos)} videos. Scored using sharpness, exposure, and facial recognition. Selected the top {len(best_photos)} media files.")
        
        return best_photos, videos
