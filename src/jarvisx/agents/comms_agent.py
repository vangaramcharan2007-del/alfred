"""
Omnichannel Communications & Social Sentinel Agent for Alfred OS.
Responsible for:
1. DMs & Messaging across WhatsApp, Instagram, and SMS.
2. Outbound Voice & Video Calling (WhatsApp & GSM Cellular Carrier).
3. Neural Multilingual Voice Notes (Telugu, English, Hindi).
4. Automated Notification Interception & Intelligent Auto-Replies.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvisx.agents.comms")


class OmnichannelCommunicationsAgent:
    """
    Master Autonomous Communications Agent for Alfred OS.
    Manages all personal/social communication pipelines for Charan.
    """

    NAME = "OmnichannelCommunicationsAgent"
    ROLE = "Social & Communications Sentinel"
    DESCRIPTION = "Autonomous agent responsible for WhatsApp, Instagram, SMS, voice calls, voice notes, and notification auto-replies."

    def __init__(self):
        self.status = "ONLINE"
        self.message_history: List[Dict[str, Any]] = []
        self.auto_reply_enabled = False

    def send_message(self, platform: str, recipient: str, message: str) -> Dict[str, Any]:
        """Dispatches a text message across the requested platform."""
        plat = platform.lower()
        if "insta" in plat or "ig" in plat:
            from jarvisx.automation.social_actuation import send_instagram_dm
            res = send_instagram_dm(username=recipient, message=message)
        elif "sms" in plat or "text" in plat:
            from jarvisx.telephony.telephony_gateway import TelephonyGateway
            gw = TelephonyGateway.get_instance()
            res = gw.send_sms(to_number=recipient, message=message)
        else: # WhatsApp default
            from jarvisx.automation.whatsapp_actuation import send_whatsapp_live
            res = send_whatsapp_live(recipient=recipient, message=message)
            
        record = {
            "timestamp": time.time(),
            "type": "TEXT_MESSAGE",
            "platform": platform,
            "recipient": recipient,
            "message": message,
            "result": res
        }
        self.message_history.append(record)
        return res

    def send_voice_note(self, platform: str, recipient: str, message: str, language: str = "english") -> Dict[str, Any]:
        """Synthesizes an HD multilingual neural voice note and delivers it via WhatsApp/Telegram/Instagram."""
        from jarvisx.automation.social_actuation import send_whatsapp_voice_note
        res = send_whatsapp_voice_note(recipient=recipient, message=message, language=language)
        record = {
            "timestamp": time.time(),
            "type": "VOICE_NOTE",
            "platform": platform,
            "recipient": recipient,
            "language": language,
            "message": message,
            "result": res
        }
        self.message_history.append(record)
        return res

    def place_call(self, platform: str, recipient: str, speech_text: str = "") -> Dict[str, Any]:
        """Places a voice call via WhatsApp or GSM cellular carrier."""
        plat = platform.lower()
        if "whats" in plat or "wa" in plat:
            from jarvisx.automation.social_actuation import call_whatsapp_voice
            res = call_whatsapp_voice(recipient=recipient)
        else: # Cellular carrier call
            from jarvisx.telephony.telephony_gateway import TelephonyGateway
            gw = TelephonyGateway.get_instance()
            res = gw.place_live_carrier_call(to_number=recipient, say_text=speech_text)
            
        record = {
            "timestamp": time.time(),
            "type": "VOICE_CALL",
            "platform": platform,
            "recipient": recipient,
            "speech_text": speech_text,
            "result": res
        }
        self.message_history.append(record)
        return res

    async def auto_reply_to_notification(self, sender: str, incoming_text: str, platform: str = "WhatsApp") -> Dict[str, Any]:
        """Autonomously crafts and dispatches a polite AI auto-reply on Charan's behalf."""
        from jarvisx.organism import get_organism
        brain = get_organism().brain
        
        prompt = f"""You are Alfred, Charan's loyal AI butler.
Charan is currently busy. An incoming notification arrived from {sender} on {platform}:
"{incoming_text}"

Draft a short, 1-sentence polite reply letting them know Charan is occupied and will respond shortly.
Reply:"""
        draft = await brain.think(prompt)
        
        return {
            "status": "AUTO_REPLY_DRAFTED",
            "sender": sender,
            "platform": platform,
            "draft_reply": draft
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent": self.NAME,
            "status": self.status,
            "total_dispatched": len(self.message_history),
            "supported_platforms": ["WhatsApp", "Instagram", "GSM SMS", "GSM Carrier Voice", "WhatsApp Voice Call"]
        }


# Singleton accessor
_comms_agent: Optional[OmnichannelCommunicationsAgent] = None

def get_comms_agent() -> OmnichannelCommunicationsAgent:
    global _comms_agent
    if _comms_agent is None:
        _comms_agent = OmnichannelCommunicationsAgent()
    return _comms_agent
