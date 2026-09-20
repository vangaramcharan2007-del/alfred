import os
import subprocess
import time

def restart():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vbs_path = os.path.join(project_root, "scripts", "start_auto_wake_sentinel.vbs")
    
    # Fast kill existing pythonw processes
    subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe"], capture_output=True)
    time.sleep(0.5)
    
    # Launch new sentinel via VBS (invisible pythonw detached)
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    subprocess.Popen(
        ["wscript.exe", vbs_path],
        cwd=project_root,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True
    )
    print("[OK] Upgraded Naruto Auto-Wake Sentinel restarted in background.")

if __name__ == "__main__":
    restart()
