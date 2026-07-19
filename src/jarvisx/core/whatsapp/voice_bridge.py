import logging
from typing import Dict, Any

from jarvisx.core.whatsapp.manager import WhatsAppAutomationManager

logger = logging.getLogger(__name__)

class WhatsAppVoiceBridge:
    """Bridges voice intents to WhatsApp automation actions."""
    
    def __init__(self, manager: WhatsAppAutomationManager):
        self.manager = manager
        
    def handle_intent(self, intent: str, text: str) -> str:
        """
        Handles voice intents mapped to WhatsApp actions.
        Returns the text response for TTS.
        """
        if intent == "WHATSAPP_START_MONITOR":
            self.manager.start()
            return "I am now monitoring WhatsApp for incoming Word documents."
            
        elif intent == "WHATSAPP_PAUSE_MONITOR":
            self.manager.pause()
            return "Document automation is now paused."
            
        elif intent == "WHATSAPP_RESUME_MONITOR":
            self.manager.resume()
            return "Document automation has been resumed."
            
        elif intent == "WHATSAPP_STATS":
            count = self.manager.files_converted_today
            if count == 0:
                return "I haven't converted any documents today."
            elif count == 1:
                return "I have converted one Word document into an Excel workbook today."
            else:
                return f"I have converted {count} Word documents into Excel workbooks today."
                
        elif intent == "WHATSAPP_CONVERT_LATEST":
            # For demonstration, trigger process manually on latest file in Inbox
            new_file = self.manager.listener.check_for_new_file()
            if new_file:
                # Run in background to not block voice
                import threading
                threading.Thread(target=self.manager.process_file, args=(new_file,), daemon=True).start()
                return "Processing the latest document now."
            else:
                return "I didn't find any new Word documents to convert."
                
        return "I'm not sure how to handle that document request."
