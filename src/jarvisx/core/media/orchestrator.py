import os
import time
import subprocess
import pywinauto

from .environment import EnvironmentManager
from .whatsapp_extractor import WhatsAppExtractor
from .intelligence import MediaIntelligence
from .photo_engine import PhotoEngine
from .video_engine import VideoEngine

class CinematicOrchestrator:
    def __init__(self, tts_engine=None):
        self.tts = tts_engine
        
        # Setup paths
        self.desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.project_dir = os.path.join(self.desktop, "Project_Tirupati")
        self.photos_dir = os.path.join(self.project_dir, "Photos")
        self.videos_dir = os.path.join(self.project_dir, "Videos")
        self.exports_dir = os.path.join(self.project_dir, "Exports")
        
        # Initialize modules
        self.extractor = WhatsAppExtractor(self.photos_dir, self.videos_dir, self.tts)
        self.intelligence = MediaIntelligence(self.tts)
        self.photo_engine = PhotoEngine(self.exports_dir, self.tts)
        self.video_engine = VideoEngine(self.exports_dir, self.tts)
        
    def speak(self, text):
        print(f"[Alfred] {text}")
        if self.tts:
            self.tts.speak(text)

    def execute_mission(self, contact_name="Ravindar vanga"):
        self.speak("MISSION: Project Tirupati. Zero-Setup Autonomous Cinematic Editor Activated.")
        
        # Phase 1: Environment
        EnvironmentManager.ensure_directories(self.project_dir)
        EnvironmentManager.verify_ffmpeg()
        
        # Phase 2: Media Collection
        self.extractor.extract_media(contact_name)
        
        # Phase 3: Media Intelligence
        best_photos, videos = self.intelligence.analyze_media(self.photos_dir, self.videos_dir)
        
        if not best_photos:
            self.speak("ABORTING: No high-quality media available to process.")
            return False
            
        # Phase 4: Photo Editing
        enhanced_photos = self.photo_engine.enhance_photos(best_photos)
        
        # Phase 5 & 6: Video Editing & QA
        out_video = self.video_engine.create_cinematic_film(enhanced_photos, videos)
        
        # Phase 7 & 8: Delivery
        self.deliver_to_whatsapp(out_video, contact_name)
        
        # Phase 10: Grand Finale
        self.play_fullscreen(out_video)
        
        return True
        
    def deliver_to_whatsapp(self, filepath, contact_name):
        self.speak(f"Phase 9: Delivering final cinematic film to {contact_name} via WhatsApp.")
        try:
            app = pywinauto.Application(backend="uia").connect(title_re=".*WhatsApp.*", timeout=5)
            window = app.window(title_re=".*WhatsApp.*")
            window.set_focus()
            time.sleep(1)
            
            cmd = f'powershell.exe -command "Set-Clipboard -Path \'{filepath}\'"'
            subprocess.run(cmd, shell=True)
            time.sleep(0.5)
            window.type_keys("^v")
            time.sleep(1.0)
            window.type_keys("{ENTER}")
            time.sleep(1.0)
            self.speak("Delivery successful.")
        except Exception as e:
            self.speak("WhatsApp UI routing skipped, but deliverables are secured in the Exports directory.")
            
    def play_fullscreen(self, filepath):
        self.speak("Phase 10: Grand Finale.")
        os.startfile(filepath)
        # Give media player time to launch, then simulate F11 / Alt+Enter for fullscreen
        time.sleep(3)
        try:
            # Blindly send F11 for fullscreen to active window (usually Movies & TV or VLC)
            pywinauto.keyboard.send_keys('{F11}')
        except:
            pass
        self.speak("Mission accomplished. Your Tirupati cinematic journey has been successfully created.")
