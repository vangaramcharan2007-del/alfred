"""
Remote Uplink Gateway — Telegram/WhatsApp Bridge.
Allows you to command Jarvis remotely from your phone.
"""
import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

class RemoteUplink:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.bot_token = "MOCK_TELEGRAM_TOKEN"
        self.authorized_chat_id = "USER_CHAT_ID"

    def _poll_messages(self):
        """Simulates polling a Telegram/WhatsApp API for remote commands."""
        logger.info("[RemoteUplink] Listening for remote commands via secure gateway...")
        
        while self._running:
            # In production: Use python-telegram-bot or WhatsApp Web.js
            # 1. Fetch updates
            # 2. Check if chat_id == authorized_chat_id
            # 3. Route text to MultiModelRouter
            # 4. Send response back to chat
            time.sleep(5)
            
    def simulate_incoming_message(self, text: str):
        """Simulate a message arriving from your phone."""
        logger.info(f"[RemoteUplink] 📱 Received remote message: '{text}'")
        try:
            from jarvisx.core.multi_model_router import MultiModelRouter
            res = MultiModelRouter.get_instance().route_and_call(text)
            reply = res.get("response", "Error processing remote command.")
            logger.info(f"[RemoteUplink] 📱 Replied: '{reply[:50]}...'")
        except Exception as e:
            logger.error(f"[RemoteUplink] Routing failed: {e}")

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._poll_messages, daemon=True, name="RemoteUplink")
        self._thread.start()
        
    def stop(self):
        self._running = False
