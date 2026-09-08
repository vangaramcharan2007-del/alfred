"""
Async Human-in-the-Loop Pager for Unattended Autonomy in Jarvis X.
Escalates roadblocks (2FA, SMS OTPs, CAPTCHAs, destructive approvals) to the user
via Windows native toasts, webhooks (Telegram/Discord), and terminal chimes.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("jarvisx.async_pager")


@dataclass
class PagerAlert:
    title: str
    message: str
    urgency: str  # "INFO", "WARNING", "CRITICAL_ACTION_REQUIRED"
    requires_input: bool = False
    context_data: Optional[Dict[str, Any]] = None
    timestamp: float = 0.0


class AsyncPager:
    """Outbound paging mechanism for unattended agent tasks."""

    _instance: Optional[AsyncPager] = None

    @classmethod
    def get_instance(cls) -> AsyncPager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.webhook_url = os.environ.get("JARVISX_ALERT_WEBHOOK", "")
        self.telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    def send_windows_toast(self, title: str, message: str) -> bool:
        """Triggers a native Windows Toast notification."""
        if sys.platform != "win32":
            return False

        safe_title = title.replace('"', '`"')
        safe_msg = message.replace('"', '`"')
        # PowerShell script using Windows.UI.Notifications
        ps_script = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; "
            "$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
            "$textNodes = $template.GetElementsByTagName('text'); "
            f"$textNodes.Item(0).AppendChild($template.CreateTextNode('{safe_title}')) > $null; "
            f"$textNodes.Item(1).AppendChild($template.CreateTextNode('{safe_msg}')) > $null; "
            "$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Jarvis X').Show($toast)"
        )
        try:
            subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception as e:
            logger.debug(f"[AsyncPager] Toast notification error: {e}")
            return False

    def send_webhook(self, title: str, message: str, urgency: str) -> bool:
        """Sends alert payload to configured webhook (Discord, Telegram, or generic HTTP)."""
        # 1. Telegram direct
        if self.telegram_bot_token and self.telegram_chat_id:
            try:
                tg_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                payload = json.dumps({
                    "chat_id": self.telegram_chat_id,
                    "text": f"🚨 *{title}* [{urgency}]\n{message}",
                    "parse_mode": "Markdown",
                }).encode("utf-8")
                req = urllib.request.Request(tg_url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=3.0):
                    return True
            except Exception as e:
                logger.debug(f"[AsyncPager] Telegram dispatch note: {e}")

        # 2. Generic / Discord Webhook
        if self.webhook_url:
            try:
                payload = json.dumps({
                    "content": f"**[Jarvis X] {title}** ({urgency})\n{message}",
                    "title": title,
                    "message": message,
                    "urgency": urgency,
                }).encode("utf-8")
                req = urllib.request.Request(self.webhook_url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=3.0):
                    return True
            except Exception as e:
                logger.debug(f"[AsyncPager] Webhook dispatch note: {e}")

        return False

    def page_user(
        self,
        title: str,
        message: str,
        urgency: str = "CRITICAL_ACTION_REQUIRED",
        requires_input: bool = False,
    ) -> PagerAlert:
        """Dispatches multi-channel notification to bring user back into loop."""
        alert = PagerAlert(
            title=title,
            message=message,
            urgency=urgency,
            requires_input=requires_input,
            timestamp=time.time(),
        )

        logger.warning(f"[AsyncPager] PAGING USER: [{urgency}] {title} - {message}")

        # Play terminal chime / print banner
        try:
            if sys.platform == "win32":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

        # Windows toast
        self.send_windows_toast(title, message)

        # Webhook
        self.send_webhook(title, message, urgency)

        return alert
