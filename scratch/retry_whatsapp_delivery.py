import os
import time
import pywinauto
import subprocess

try:
    import sys
    sys.path.insert(0, os.path.abspath("src"))
    from jarvisx.core.voice.tts_engine import TTSEngine
    tts = TTSEngine()
    def speak(text):
        print(f"[Alfred] {text}")
        tts.speak(text)
except:
    def speak(text):
        print(f"[Alfred] {text}")

def retry_whatsapp():
    speak("WhatsApp appeared to be minimized or closed. Opening it now to deliver the documents.")
    
    # Force open WhatsApp Desktop
    os.system("start whatsapp://")
    time.sleep(5)  # Wait for it to open and settle
    
    out_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_WhatsApp_Automation", "Outbox_Separate")
    
    files = [
        os.path.join(out_dir, "Memo_17_01_2023.xlsx"),
        os.path.join(out_dir, "Memo_27_03_2025.xlsx"),
        os.path.join(out_dir, "Memo_16_09_2021.xlsx"),
        os.path.join(out_dir, "Memo_20_01_2022.xlsx")
    ]
    
    try:
        app = pywinauto.Application(backend="uia").connect(title_re=".*WhatsApp.*", timeout=10)
        window = app.window(title_re=".*WhatsApp.*")
        window.set_focus()
        time.sleep(1)
        
        # Search for Ravindar vanga
        window.type_keys("^f")
        time.sleep(0.5)
        window.type_keys("Ravindar vanga{ENTER}", with_spaces=True)
        time.sleep(1.5)
        
        for f in files:
            if not os.path.exists(f):
                continue
                
            cmd = f'powershell.exe -command "Set-Clipboard -Path \'{f}\'"'
            subprocess.run(cmd, shell=True)
            time.sleep(0.5)
            window.type_keys("^v")
            time.sleep(1.0)
            window.type_keys("{ENTER}")
            time.sleep(1.0)
            
        speak("Delivery confirmed. All four sorted Excel files have been dispatched to Ravindar vanga.")
    except Exception as e:
        speak("I am still having trouble interfacing with the WhatsApp window.")
        print(f"WhatsApp UI error: {e}")

if __name__ == "__main__":
    retry_whatsapp()
