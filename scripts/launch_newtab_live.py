import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWTAB_PATH = os.path.join(PROJECT_ROOT, "newtab", "index.html")

BRAVE = r"C:\Users\vanga\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def find_browser():
    for candidate in [BRAVE, EDGE, CHROME]:
        if os.path.exists(candidate):
            return candidate
    return None

def launch():
    browser = find_browser()
    file_url = f"file:///{NEWTAB_PATH.replace(os.sep, '/')}"
    args = f'--app="{file_url}" --start-maximized --autoplay-policy=no-user-gesture-required --allow-file-access-from-files'
    print(f"[LAUNCH] Browser: {browser}")
    print(f"[LAUNCH] URL: {file_url}")
    
    if browser:
        # Launch via Windows Shell (Explorer) so it surfaces immediately on the user's interactive desktop
        ps_cmd = f"(New-Object -ComObject Shell.Application).ShellExecute('{browser}', '{args}', '', 'open', 1)"
        try:
            subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            print("[OK] Opened live on user's display via Explorer ShellExecute.")
        except Exception as e:
            print(f"[WARN] Explorer launch: {e}, falling back to direct process")
            subprocess.Popen([browser, f'--app={file_url}', '--start-maximized'])
    else:
        os.startfile(file_url)
        print("[OK] Opened via default shell.")

if __name__ == "__main__":
    launch()
