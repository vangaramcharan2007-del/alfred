import ctypes
from ctypes import wintypes

class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', ctypes.c_byte),
        ('BatteryFlag', ctypes.c_byte),
        ('BatteryLifePercent', ctypes.c_byte),
        ('SystemStatusFlag', ctypes.c_byte),
        ('BatteryLifeTime', wintypes.DWORD),
        ('BatteryFullLifeTime', wintypes.DWORD),
    ]

def get_battery_info():
    status = SYSTEM_POWER_STATUS()
    if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
        percent = int(status.BatteryLifePercent)
        is_charging = bool(status.ACLineStatus == 1)
        return {
            "percent": percent if percent <= 100 else 100,
            "charging": is_charging
        }
    return {"percent": 100, "charging": True}

if __name__ == "__main__":
    b = get_battery_info()
    print(f"BATTERY_RESULT: percent={b['percent']} charging={b['charging']}")
