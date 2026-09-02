"""
Jarvis X — Autonomous Real-Time Reminder, Alarm & Notification Scheduling Engine.
Manages timed reminders, timers, alarms, and alerts with vocal speech and Windows toast notifications.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import re
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.automation.reminder_engine")


class ReminderEngine:
    """
    Zero-lag background reminder daemon and notification scheduler.
    Schedules reminders by relative delay or exact clock time (e.g. '5:24 PM', 'in 10 minutes').
    Fires spoken vocal alert + native Windows toast notification + neural event pulse.
    """

    _instance: Optional[ReminderEngine] = None
    _lock = threading.Lock()

    def __init__(self, storage_path: str = "var/reminders.json"):
        self.storage_path = Path(storage_path)
        self.reminders: List[Dict[str, Any]] = []
        self._sentinel_running = False
        self._sentinel_thread: Optional[threading.Thread] = None
        self._load()
        self.start_sentinel()

    @classmethod
    def get_instance(cls) -> ReminderEngine:
        with cls._lock:
            if cls._instance is None:
                cls._instance = ReminderEngine()
            return cls._instance

    def _load(self) -> None:
        """Load pending reminders from disk."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.reminders = json.load(f)
        except Exception as e:
            logger.warning(f"[ReminderEngine] Failed to load reminders: {e}")
            self.reminders = []

    def _save(self) -> None:
        """Persist active reminders to disk."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.reminders, f, indent=2)
        except Exception as e:
            logger.warning(f"[ReminderEngine] Failed to save reminders: {e}")

    def parse_target_time(self, time_spec: str, date_spec: Optional[str] = None) -> datetime.datetime:
        """
        Intelligently parse natural time expressions:
          - '524 pm', '5:24 pm', '5.24pm', '17:24', '5pm', '5:24'
          - 'in 10 minutes', 'in 5 mins', 'in 1 hour', 'in 30 seconds', '10m'
        """
        now = datetime.datetime.now()
        ts = str(time_spec).strip().lower()

        # 1. Relative offset (e.g. "in 10 minutes", "in 2 hours", "in 30 seconds", "10m", "5min")
        rel_match = re.search(r'(?:in\s+)?(\d+(?:\.\d+)?)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hr|hour|hours|d|day|days)\b', ts)
        if rel_match:
            val = float(rel_match.group(1))
            unit = rel_match.group(2).lower()
            if unit.startswith("s"):
                return now + datetime.timedelta(seconds=val)
            elif unit.startswith("m"):
                return now + datetime.timedelta(minutes=val)
            elif unit.startswith("h"):
                return now + datetime.timedelta(hours=val)
            elif unit.startswith("d"):
                return now + datetime.timedelta(days=val)

        # 2. Number only relative (e.g. if time_spec is "10" minutes)
        if ts.isdigit() and int(ts) > 0 and int(ts) <= 180:
            return now + datetime.timedelta(minutes=int(ts))

        # 3. Exact Clock Time (e.g. '524 pm', '5:24 pm', '5.24pm', '17:24', '5:24', '5pm')
        # Clean spacing: '524 pm' -> '5:24 pm'
        digits_ampm = re.match(r'^(\d{1,2})(\d{2})\s*(am|pm)$', ts)
        if digits_ampm:
            ts = f"{digits_ampm.group(1)}:{digits_ampm.group(2)} {digits_ampm.group(3)}"

        # Clean '5pm' -> '5:00 pm'
        hour_ampm = re.match(r'^(\d{1,2})\s*(am|pm)$', ts)
        if hour_ampm:
            ts = f"{hour_ampm.group(1)}:00 {hour_ampm.group(2)}"

        # Clean '5.24 pm' -> '5:24 pm'
        ts = ts.replace(".", ":")

        # Try various standard time formats
        for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M", "%I %p", "%I%p", "%H:%M:%S"):
            try:
                parsed_time = datetime.datetime.strptime(ts, fmt).time()
                # Target date is today by default
                target_dt = datetime.datetime.combine(now.date(), parsed_time)
                
                # If date_spec is tomorrow or target time has passed today without explicit date
                if date_spec and "tomorrow" in date_spec.lower():
                    target_dt += datetime.timedelta(days=1)
                elif target_dt < now - datetime.timedelta(minutes=1):
                    # Time has already passed today, assume tomorrow
                    target_dt += datetime.timedelta(days=1)
                return target_dt
            except ValueError:
                continue

        # Fallback: default to 10 minutes from now if unparseable
        return now + datetime.timedelta(minutes=10)

    def set_reminder(
        self,
        message: str,
        time_spec: str = "10 minutes",
        date_spec: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Schedule a new reminder."""
        target_dt = self.parse_target_time(time_spec, date_spec)
        target_epoch = target_dt.timestamp()
        now_epoch = time.time()
        diff_sec = max(0, int(target_epoch - now_epoch))

        # Format countdown
        if diff_sec >= 3600:
            hrs = diff_sec // 3600
            mins = (diff_sec % 3600) // 60
            countdown_str = f"in {hrs}h {mins}m"
        elif diff_sec >= 60:
            mins = diff_sec // 60
            secs = diff_sec % 60
            countdown_str = f"in {mins} minute{'s' if mins > 1 else ''}" + (f" {secs}s" if secs else "")
        else:
            countdown_str = f"in {diff_sec} seconds"

        rem_id = f"rem_{uuid.uuid4().hex[:6]}"
        display_time = target_dt.strftime("%I:%M %p on %A, %B %d") if target_dt.date() != datetime.date.today() else target_dt.strftime("%I:%M %p today")

        record = {
            "id": rem_id,
            "message": message,
            "time_spec": time_spec,
            "target_epoch": target_epoch,
            "target_iso": target_dt.isoformat(),
            "display_time": display_time,
            "countdown": countdown_str,
            "status": "PENDING",
            "created_at": datetime.datetime.now().isoformat(),
        }

        self.reminders.append(record)
        self._save()

        logger.info(f"[ReminderEngine] Scheduled reminder '{rem_id}': '{message}' for {display_time} ({countdown_str})")
        return {
            "status": "success",
            "id": rem_id,
            "message": message,
            "display_time": display_time,
            "countdown": countdown_str,
            "target_iso": target_dt.isoformat(),
        }

    def list_reminders(self, pending_only: bool = True) -> List[Dict[str, Any]]:
        """List active scheduled reminders."""
        if pending_only:
            return [r for r in self.reminders if r.get("status") == "PENDING"]
        return list(self.reminders)

    def cancel_reminder(self, reminder_id_or_keyword: str) -> Dict[str, Any]:
        """Cancel a reminder by ID or matching message keyword."""
        kw = reminder_id_or_keyword.lower().strip()
        cancelled = []
        for r in self.reminders:
            if r.get("status") == "PENDING" and (r.get("id") == kw or kw in r.get("message", "").lower()):
                r["status"] = "CANCELLED"
                cancelled.append(r)
        self._save()
        if cancelled:
            return {"status": "success", "cancelled_count": len(cancelled), "cancelled": cancelled}
        return {"status": "failed", "error": f"No matching pending reminder found for '{reminder_id_or_keyword}'."}

    def start_sentinel(self) -> None:
        """Start the background reminder monitoring sentinel loop."""
        if self._sentinel_running:
            return
        self._sentinel_running = True
        self._sentinel_thread = threading.Thread(target=self._sentinel_loop, daemon=True, name="AlfredReminderSentinel")
        self._sentinel_thread.start()
        logger.info("[ReminderEngine] Sentinel background thread online.")

    def _sentinel_loop(self) -> None:
        """Continuously check for due reminders every second."""
        while self._sentinel_running:
            try:
                now_epoch = time.time()
                for r in self.reminders:
                    if r.get("status") == "PENDING" and r.get("target_epoch", 0) <= now_epoch:
                        r["status"] = "FIRED"
                        self._save()
                        self._fire_reminder(r)
            except Exception as e:
                logger.error(f"[ReminderEngine] Sentinel sweep error: {e}")
            time.sleep(1.0)

    def _fire_reminder(self, record: Dict[str, Any]) -> None:
        """Execute vocal voice announcement and desktop toast alert when reminder is due."""
        msg = record.get("message", "You have a scheduled reminder.")
        logger.info(f"[ReminderEngine] 🔔 FIRING REMINDER: '{msg}'")

        # 1. Native Windows Desktop Toast Notification
        try:
            from jarvisx.automation.real_notifications import RealNotificationEngine
            notifier = RealNotificationEngine()
            notifier.send_desktop_alert(
                title="⏰ Alfred Reminder",
                message=msg,
                timeout_seconds=5
            )
        except Exception as e:
            logger.debug(f"[ReminderEngine] Toast dispatch exception: {e}")

        # 2. Vocal TTS Announcement
        try:
            from jarvisx.organism import get_organism
            org = get_organism()
            salutation = "Sir" if org.persona == "ALFRED" else "Boss"
            speech_text = f"Pardon the interruption, {salutation}. Here is your scheduled reminder: {msg}"
            org.mouth.speak(speech_text, blocking=False)
            
            # Pulse neural bus
            import asyncio
            try:
                asyncio.run(org.nerves.pulse("reminder_fired", {"id": record.get("id"), "message": msg}))
            except Exception:
                pass
        except Exception as e:
            logger.debug(f"[ReminderEngine] Speech announcement exception: {e}")


# Singleton accessor
def get_reminder_engine() -> ReminderEngine:
    return ReminderEngine.get_instance()
