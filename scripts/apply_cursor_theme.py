"""
Jarvis X - Cursor Scheme Switcher
Applies cursor themes dynamically using Windows Win32 API SPI_SETCURSORS.
"""
import winreg
import ctypes
import sys

user32 = ctypes.windll.user32
SPI_SETCURSORS = 0x0057

def apply_scheme(scheme_name):
    # 1. Read scheme definitions from HKLM
    schemes_key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE, 
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Control Panel\Cursors\Schemes"
    )
    try:
        val, typ = winreg.QueryValueEx(schemes_key, scheme_name)
    except FileNotFoundError:
        print(f"[!] Scheme '{scheme_name}' not found.")
        return False
        
    parts = val.split(",")
    # Mapping of cursor slots
    slots = [
        "Arrow", "Help", "AppStarting", "Wait", "Crosshair", "IBeam", 
        "NWPen", "No", "SizeNS", "SizeWE", "SizeNWSE", "SizeNESW", 
        "SizeAll", "UpArrow", "Hand"
    ]
    
    # 2. Write to HKCU\Control Panel\Cursors
    hkcu_key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, 
        r"Control Panel\Cursors", 
        0, 
        winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(hkcu_key, "", 0, winreg.REG_SZ, scheme_name)
    
    for idx, slot in enumerate(slots):
        path = parts[idx] if idx < len(parts) else ""
        winreg.SetValueEx(hkcu_key, slot, 0, winreg.REG_EXPAND_SZ, path)
        
    winreg.CloseKey(hkcu_key)
    winreg.CloseKey(schemes_key)
    
    # 3. Broadcast SPI_SETCURSORS
    user32.SystemParametersInfoW(SPI_SETCURSORS, 0, 0, 0)
    print(f"[+] Successfully applied cursor scheme: '{scheme_name}'!")
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Windows Black"
    apply_scheme(target)
