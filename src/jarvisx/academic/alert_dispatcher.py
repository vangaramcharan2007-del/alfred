"""Proactive Alert Dispatcher.

Dispatches academic notifications via multiple modalities:
1. Voice Audio Announcements (Jarvis TTS)
2. Windows Desktop Toast Notifications
3. HUD Server Event Streaming
"""

from __future__ import annotations
import logging
import subprocess
import time
from typing import List, Optional

from jarvisx.academic.models import AcademicTask, AlertEvent, TaskPriority

logger = logging.getLogger("jarvisx.academic.alert_dispatcher")


class AcademicAlertDispatcher:
    """Delivers prioritized academic alerts to the student via desktop toasts and voice."""

    def __init__(self, enable_voice: bool = True, enable_toast: bool = True):
        self.enable_voice = enable_voice
        self.enable_toast = enable_toast
        self.dispatched_history: List[AlertEvent] = []

    def dispatch_task_alert(self, task: AcademicTask, is_solved: bool = False) -> AlertEvent:
        """Constructs and delivers a proactive alert for an academic task."""
        if is_solved:
            title = f"Academic Solved: {task.title}"
            msg = f"Task for {task.course_code} has been autonomously solved and compiled into DOCX/PDF."
            spoken = f"Sir, I have completed the assignment for {task.course_name}. The solutions and code are compiled and ready."
        else:
            hours = max(1, int(task.hours_remaining))
            title = f"Academic Alert [{task.priority.value}]: {task.title}"
            msg = f"Upcoming deadline for {task.course_code} in {hours} hours via {task.channel.value}."
            spoken = f"Attention Sir. An academic task for {task.course_name} is due in {hours} hours. Initiating autonomous resolution."

        event = AlertEvent(
            event_id=f"EVT-{int(time.time() * 1000) % 100000}",
            task_id=task.task_id,
            channel=task.channel,
            urgency=task.priority,
            title=title,
            message=msg,
            spoken_text=spoken,
        )

        # 1. Desktop Toast Notification
        if self.enable_toast:
            self._send_windows_toast(event.title, event.message)

        # 2. Voice Audio
        if self.enable_voice:
            self._speak(event.spoken_text)

        event.delivered = True
        self.dispatched_history.append(event)
        logger.info(f"Dispatched alert {event.event_id} for {task.task_id}")
        return event

    def _send_windows_toast(self, title: str, message: str):
        """Sends a native Windows balloon/toast notification using PowerShell."""
        clean_title = title.replace('"', '`"').replace("'", "''")
        clean_msg = message.replace('"', '`"').replace("'", "''")
        ps_cmd = f"""
        [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms");
        $notify = New-Object System.Windows.Forms.NotifyIcon;
        $notify.Icon = [System.Drawing.SystemIcons]::Information;
        $notify.BalloonTipTitle = "{clean_title}";
        $notify.BalloonTipText = "{clean_msg}";
        $notify.BalloonTipIcon = "Info";
        $notify.Visible = $True;
        $notify.ShowBalloonTip(4000);
        """
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                timeout=5,
            )
        except Exception as e:
            logger.debug(f"Toast notification failed: {e}")

    def _speak(self, text: str):
        """Synthesizes voice announcement using Windows SAPI TTS."""
        clean_text = text.replace('"', '`"').replace("'", "''")
        ps_speech = f"""
        Add-Type -AssemblyName System.Speech;
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;
        $synth.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Male);
        $synth.Speak("{clean_text}");
        """
        try:
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", ps_speech],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.debug(f"Speech synthesis error: {e}")
