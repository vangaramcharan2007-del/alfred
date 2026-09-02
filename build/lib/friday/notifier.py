"""
Friday Notifier - Real Windows system notifications.
Uses ctypes MessageBox as universal fallback (works on all Windows).
"""
from __future__ import annotations
import ctypes
import subprocess
from typing import List


def notify(title: str, message: str) -> bool:
    """Send a real Windows notification. Returns True on success."""
    # Try PowerShell toast notification first (Windows 10+)
    try:
        ps_script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null
$template = @"
<toast>
  <visual>
    <binding template="ToastGeneric">
      <text>{title}</text>
      <text>{message}</text>
    </binding>
  </visual>
</toast>
"@
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Friday")
$notifier.Show($toast)
"""
        r = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            return True
    except Exception:
        pass

    # Fallback: Windows MessageBox (always works)
    try:
        MB_ICONINFORMATION = 0x40
        MB_SYSTEMMODAL = 0x1000
        ctypes.windll.user32.MessageBoxW(
            0, message, f"Friday: {title}", MB_ICONINFORMATION | MB_SYSTEMMODAL
        )
        return True
    except Exception:
        return False


def send_alerts(alerts: List[str]) -> int:
    """Send multiple alerts as a single notification."""
    if not alerts:
        return 0

    combined = "\n".join(f"- {a}" for a in alerts[:5])
    title = f"{len(alerts)} Reminder{'s' if len(alerts) > 1 else ''}"
    notify(title, combined)
    return len(alerts)
