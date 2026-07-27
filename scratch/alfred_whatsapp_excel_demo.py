import pandas as pd
import os
import pyttsx3
import time
import pyautogui
import webbrowser
import re

def main():
    print('=============================================')
    print('  ALFRED: EXCEL GENERATION & WHATSAPP DEMO   ')
    print('=============================================')
    
    # 1. Voice setup
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    for v in engine.getProperty('voices'):
        if 'david' in v.name.lower() or 'male' in v.name.lower():
            engine.setProperty('voice', v.id)
            break

    def speak(text):
        print(f"\n[Alfred Voice]: {text}")
        engine.say(text)
        engine.runAndWait()

    speak("Right away sir. I am parsing the employee data from the PDFs into Excel files now.")

    # 2. Parse Data
    try:
        with open('scratch/whatsapp_data.txt', 'r', encoding='utf-8') as f:
            data = f.read()
    except Exception as e:
        speak("I could not find the raw data file.")
        return

    sections = data.split('\n\n')
    files = []

    for section in sections:
        lines = section.strip().split('\n')
        if len(lines) < 3: continue
        title = lines[0].replace('File 1:', '').replace('File 2:', '').replace('File 3:', '').replace(':', '').replace('.pdf', '').strip()
        
        records = []
        for line in lines[2:]:
            parts = re.split(r'\s{2,}|\t', line.strip())
            if len(parts) >= 3:
                records.append({
                    "Name": parts[0],
                    "Date of Birth": parts[1],
                    "Date of Joining": parts[2]
                })
        
        if records:
            df = pd.DataFrame(records)
            # Clean filename
            clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            filename = f"scratch/{clean_title.replace(' ', '_')}.xlsx"
            df.to_excel(filename, index=False)
            files.append(os.path.abspath(filename))
            print(f"[+] Created: {filename} with {len(records)} records.")
        
    speak(f"Successfully generated {len(files)} Excel files. Initializing WhatsApp Web interface.")

    # 3. WhatsApp Automation
    webbrowser.open("https://web.whatsapp.com")
    speak("Opening WhatsApp Web. Waiting 15 seconds for the page to load.")
    time.sleep(15)

    speak("Searching for Ravindar Vanga.")
    # Press Ctrl+Alt+/ to search in WhatsApp Web
    pyautogui.hotkey('ctrl', 'alt', '/')
    time.sleep(2)
    pyautogui.write("ravindar vanga")
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)

    speak("Typing out the transmission message.")
    pyautogui.write("Hello Ravindar, I have generated the 4 requested Excel files regarding the ABT AE probation commencement. ")
    time.sleep(0.5)
    pyautogui.press('enter')

    # Open the folder so the user can see the files
    speak("I am opening the folder containing the Excel files so you can review them and drag them into the chat.")
    os.startfile(os.path.abspath("scratch"))

    speak("The automation drill is complete.")
    print('\n[*] Task Finished.')

if __name__ == '__main__':
    main()
