"""
Smart Notification Engine — Proactive Desktop Alerts for Jarvis X.
Monitors system state and triggers toast notifications + voice alerts
when critical events are detected.
"""

import logging
import threading
import time
from typing import Dict, Any, List, Callable, Optional

import psutil

logger = logging.getLogger(__name__)


class SmartNotifier:
    """Proactive notification engine that watches system state and alerts the user."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "SmartNotifier":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._check_interval = 30  # seconds
        self._thresholds = {
            "battery_low": 20,
            "battery_critical": 10,
            "ram_high": 90,
            "cpu_high": 95,
        }
        self._last_alerts: Dict[str, float] = {}
        self._cooldown = 300  # 5 min between same alert type
        self._callbacks: List[Callable] = []

    def on_notification(self, callback: Callable):
        """Register a callback for notifications. callback(type, message, severity)."""
        self._callbacks.append(callback)

    def _notify(self, alert_type: str, message: str, severity: str = "warning"):
        """Fire notification if not in cooldown."""
        now = time.time()
        last = self._last_alerts.get(alert_type, 0)
        if now - last < self._cooldown:
            return

        self._last_alerts[alert_type] = now
        logger.info(f"[SmartNotifier] {severity.upper()}: {message}")

        # Desktop toast
        try:
            self._show_toast(alert_type, message)
        except Exception as e:
            logger.debug(f"Toast failed: {e}")

        # Voice alert
        try:
            from jarvisx.automation.ev_master_automation_engine import speak_ev_neural
            speak_ev_neural(message)
        except Exception:
            pass

        # HUD broadcast
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync("notification", {"type": alert_type, "message": message, "severity": severity})
        except Exception:
            pass

        # Custom callbacks
        for cb in self._callbacks:
            try:
                cb(alert_type, message, severity)
            except Exception:
                pass

    def _show_toast(self, title: str, message: str):
        """Show a Windows toast notification."""
        import subprocess
        ps_cmd = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $textNodes = $template.GetElementsByTagName("text")
        $textNodes.Item(0).AppendChild($template.CreateTextNode("JARVIS: {title}")) > $null
        $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Jarvis X").Show($toast)
        '''
        subprocess.Popen(
            ["powershell", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=0x08000000  # CREATE_NO_WINDOW
        )

    def _check_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                # Battery check
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged:
                    if battery.percent <= self._thresholds["battery_critical"]:
                        self._notify("battery_critical",
                            f"CRITICAL: Battery at {battery.percent}%! Plug in immediately, sir.",
                            "critical")
                    elif battery.percent <= self._thresholds["battery_low"]:
                        self._notify("battery_low",
                            f"Battery running low at {battery.percent}%. Consider plugging in.",
                            "warning")

                # RAM check
                ram = psutil.virtual_memory()
                if ram.percent >= self._thresholds["ram_high"]:
                    self._notify("ram_high",
                        f"RAM usage at {ram.percent}%. System may slow down.",
                        "warning")

                # CPU check
                cpu = psutil.cpu_percent(interval=1)
                if cpu >= self._thresholds["cpu_high"]:
                    self._notify("cpu_high",
                        f"CPU at {cpu}%. Heavy load detected.",
                        "warning")

            except Exception as e:
                logger.debug(f"[SmartNotifier] Check error: {e}")

            time.sleep(self._check_interval)

    def start(self):
        """Start the background monitoring loop."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True, name="SmartNotifier")
        self._thread.start()
        logger.info("[SmartNotifier] Monitoring started")

    def stop(self):
        """Stop monitoring."""
        self._running = False

    def send_custom(self, message: str, severity: str = "info"):
        """Manually trigger a notification."""
        self._notify("custom", message, severity)
