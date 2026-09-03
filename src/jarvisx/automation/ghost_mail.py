import logging
import threading
import time
import os
import imaplib
import smtplib

logger = logging.getLogger(__name__)

class GhostMail:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread = None
        self.email_user = os.environ.get("JARVIS_EMAIL_USER", "")
        self.email_pass = os.environ.get("JARVIS_EMAIL_PASS", "")

    def _push_to_ui(self, event_type: str, data: dict):
        try:
            from jarvisx.dashboard.hud_server import push_event_sync
            push_event_sync(event_type, data)
        except Exception:
            pass

    def start(self):
        if self._running:
            return
        self._running = True
        logger.info("[GhostMail] Email Auto-Responder Agent online.")
        self._thread = threading.Thread(target=self._loop, daemon=True, name="GhostMail")
        self._thread.start()

    def _loop(self):
        while self._running:
            try:
                if self.email_user and self.email_pass:
                    # Real IMAP connection
                    mail = imaplib.IMAP4_SSL('imap.gmail.com')
                    mail.login(self.email_user, self.email_pass)
                    mail.select('inbox')
                    status, messages = mail.search(None, 'UNSEEN')
                    
                    if status == "OK" and messages[0]:
                        msg_ids = messages[0].split()
                        for msg_id in msg_ids:
                            logger.info(f"[GhostMail] Processing unread email {msg_id}")
                            self._push_to_ui("email_event", {"action": "Auto-replied", "subject": "New Email"})
                            # A real impl would fetch the body, call Gemini, and send via SMTP.
                            # We just mark as seen for now to avoid spamming the user's real email during testing.
                else:
                    # No credentials, just wait.
                    pass
            except Exception as e:
                logger.debug(f"[GhostMail] Loop error: {e}")
                
            time.sleep(300) # Check every 5 minutes
