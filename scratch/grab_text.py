import pyautogui
import pyperclip
import time

def grab_screen_text():
    print("[Jarvis X]: You have 10 seconds to switch to the NPTEL Assignment tab...")
    time.sleep(10)
    
    print("[Jarvis X]: Grabbing text from screen...")
    # Click in the center of the screen just to ensure focus on the page body
    screenWidth, screenHeight = pyautogui.size()
    pyautogui.click(screenWidth / 2, screenHeight / 2)
    time.sleep(0.5)
    
    # Select All
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    
    # Copy
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1.0)
    
    # Deselect
    pyautogui.click(screenWidth / 2, screenHeight / 2)
    
    # Save to file
    text = pyperclip.paste()
    with open("scratch/nptel_questions.txt", "w", encoding="utf-8", errors="ignore") as f:
        f.write(text)
        
    print(f"[Jarvis X]: Successfully grabbed {len(text)} characters of text!")

if __name__ == "__main__":
    grab_screen_text()
