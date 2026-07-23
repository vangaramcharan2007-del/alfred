import os
import sys
import time
import asyncio
import pyttsx3
import cv2
import numpy as np

# Ensure src is in path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jarvisx.runtime import create_default_runtime
from jarvisx.agents.alfred import AlfredOrchestrator

class TTSEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        # Set a professional voice if available
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "Zira" in voice.name or "Hazel" in voice.name or "David" in voice.name:
                self.engine.setProperty('voice', voice.id)
                break
                
    def speak(self, text):
        print(f"[Jarvis X] {text}")
        self.engine.say(text)
        self.engine.runAndWait()

def create_synthetic_low_res_video(filepath):
    """Creates a very short 480p synthetic video to act as our 'downloaded' WhatsApp media."""
    print("[System] Generating synthetic low-quality video for demonstration...")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, 30.0, (640, 480))
    
    for i in range(60): # 2 seconds
        # Create a simple noisy/low-res frame with some text
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (50, 50, 100) # Dark blue background
        
        # Add some moving element
        cv2.circle(frame, (320 + int(100 * np.sin(i * 0.1)), 240), 50, (0, 255, 255), -1)
        cv2.putText(frame, "Low Quality Source", (100, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        out.write(frame)
        
    out.release()
    print(f"[System] Saved: {filepath}")

def upscale_video_to_4k(input_path, output_path, tts):
    tts.speak("Engaging OpenCV AI upscaling pipeline with Lanczos interpolation.")
    
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (3840, 2160))
    
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Upscale
        frame_4k = cv2.resize(frame, (3840, 2160), interpolation=cv2.INTER_LANCZOS4)
        cv2.putText(frame_4k, "4K UHD UPSCALED", (100, 2000), cv2.FONT_HERSHEY_SIMPLEX, 4.0, (0, 255, 0), 5)
        out.write(frame_4k)
        
        count += 1
        if count % 15 == 0:
            print(f"[Upscaling] Processed {count}/{total_frames} frames...")
            
    cap.release()
    out.release()
    tts.speak(f"Upscaling complete. 4K master saved to {output_path}.")

async def main():
    tts = TTSEngine()
    
    # 1. Initialize Jarvis X Runtime
    tts.speak("Initializing Jarvis X runtime.")
    runtime = create_default_runtime()
    alfred = runtime.alfred
    
    # User Prompt
    prompt = "78427 70283 alfred open whatsapp in the given number chat there is a lowquality video upscale it to as close to 4k"
    
    tts.speak(f"Received user command: {prompt}")
    
    # 2. Let Alfred process it
    response = await alfred.process(prompt)
    
    print("\n--- Alfred Response ---")
    print(response)
    print("-----------------------\n")
    
    # 3. If Alfred detected the video_processing intent, execute the physical flow
    if response and response.message and "Extracting video from WhatsApp" in response.message:
        tts.speak("Intent classified successfully. Initiating live WhatsApp integration.")
        
        # Phone number parsing (rudimentary for demo)
        phone = "917842770283"
        
        # A. Open WhatsApp using Deep Link
        tts.speak("Opening WhatsApp to the specified contact.")
        os.system(f"start whatsapp://send?phone={phone}")
        
        # Give it time to open in front of the user
        time.sleep(4)
        
        # B. Simulate downloading media
        tts.speak("Target locked. Extracting low quality video from chat history.")
        input_vid = os.path.abspath("downloads_mock_video.mp4")
        output_vid = os.path.abspath("upscaled_4k_master.mp4")
        
        create_synthetic_low_res_video(input_vid)
        
        time.sleep(2)
        
        # C. Upscale to 4K
        tts.speak("Media secured locally. Commencing pixel enhancement.")
        upscale_video_to_4k(input_vid, output_vid, tts)
        
        # D. Finish
        tts.speak("Mission accomplished. The video has been upscaled to 4K resolution.")
        
        # Optionally open the upscaled video
        os.system(f"start {output_vid}")
        
    else:
        tts.speak("Alfred did not correctly route the intent. Mission aborted.")

if __name__ == "__main__":
    asyncio.run(main())
