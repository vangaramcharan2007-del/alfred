"""
Jarvis X — Windows Startup Installer
Automatically registers the jarvisd kernel to boot invisibly on Windows startup.
"""
import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")

def install_to_startup():
    logging.info("Installing Jarvis X to Windows Startup Registry (HKCU)...")
    
    # 1. Get paths
    python_exe = sys.executable
    pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        pythonw_exe = python_exe
        
    project_dir = Path(__file__).parent.parent.parent.parent.absolute()
    jarvisd_script = project_dir / "src" / "jarvisx" / "kernel" / "jarvisd.py"
    
    if not jarvisd_script.exists():
        logging.error(f"Could not find jarvisd.py at {jarvisd_script}")
        return

    # 2. Command to run silently
    # pythonw.exe doesn't spawn a console window.
    cmd = f'"{pythonw_exe}" "{jarvisd_script}"'

    # 3. Add to Registry
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "JarvisX_Kernel", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        
        logging.info(f"✅ Success! Jarvis will now boot automatically via Registry HKCU.")
        logging.info(f"Command registered: {cmd}")
    except Exception as e:
        logging.error(f"Failed to write to registry: {e}")

if __name__ == "__main__":
    install_to_startup()
