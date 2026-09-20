import subprocess

def check():
    cmd = ["powershell", "-NoProfile", "-Command", 
           "Get-CimInstance Win32_Process -Filter \"Name like 'python%' and CommandLine like '%auto_wake_sentinel.py%'\" | Select-Object ProcessId, Name, CommandLine | Format-List"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    output = res.stdout.strip()
    if "auto_wake_sentinel" in output:
        print("[SENTINEL STATUS]: RUNNING")
        print(output)
    else:
        print("[SENTINEL STATUS]: NOT RUNNING - Starting now...")
        project_root = r"c:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x"
        vbs_path = project_root + r"\scripts\start_auto_wake_sentinel.vbs"
        subprocess.Popen(["wscript.exe", vbs_path], cwd=project_root)
        print("[SENTINEL STATUS]: Started successfully via VBS!")

if __name__ == "__main__":
    check()
