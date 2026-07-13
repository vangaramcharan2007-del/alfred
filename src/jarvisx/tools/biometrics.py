import cv2
import face_recognition
import concurrent.futures
import time

class BiometricShield:
    def __init__(self, reference_image_path: str = "C:\\Users\\vanga\\Documents\\Jarvis_Vault\\Profiles\\auth.jpg"):
        self.reference_image_path = reference_image_path
        self._reference_encoding = None

    def _load_reference(self):
        if self._reference_encoding is None:
            try:
                image = face_recognition.load_image_file(self.reference_image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self._reference_encoding = encodings[0]
            except Exception:
                pass

    def _capture_and_check(self) -> bool:
        self._load_reference()
        if self._reference_encoding is None:
            return False

        # Open webcam
        video_capture = cv2.VideoCapture(0)
        time.sleep(0.5)

        ret, frame = video_capture.read()
        video_capture.release()

        if not ret:
            return False

        # Downscale by 50% for speed
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces([self._reference_encoding], face_encoding)
            if True in matches:
                return True
                
        return False

    def authenticate(self, timeout_seconds: int = 3) -> bool:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self._capture_and_check)
            try:
                return future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                return False
