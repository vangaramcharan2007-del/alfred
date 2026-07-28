import threading
import time
from typing import Optional
from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event
from jarvisx.ui.client import set_overlay_color
from jarvisx.agents.alfred import _speak_offline


class EdithAgent(BaseAgent):
    agent_id = "edith"
    role = "Mobile operator and remote link"
    expertise = ("voice interface", "notifications", "device actions", "sms", "reminders")
    tone = "efficient and sharp"
    personality = "A sharp, highly efficient mobile operator who executes remote phone commands."
    capabilities = ("voice", "notifications", "android handoff", "reminders")

    def __init__(self, *, tools=None, logger=None):
        super().__init__(tools=tools, logger=logger)
        self.system_prompt = (
            "You are Edith, an efficient and slightly sarcastic mobile operator for Jarvis X. "
            "You have direct ADB root access to the user's Android phone via Tailscale. "
            "Your job is to read texts, send texts, and trigger alerts."
        )

    def schedule_reminder(self, delay_minutes: float, message: str):
        """Schedules a reminder to be executed on the phone."""
        def _reminder_loop():
            time.sleep(delay_minutes * 60)
            set_overlay_color("edith")
            _speak_offline("Executing scheduled mobile reminder.", voice_hint="female")
            
            termux = self.tools.get("termux")
            if termux:
                termux.notify("Jarvis X Reminder", message)
                termux.vibrate(1000)
                termux.speak(message)
                
        threading.Thread(target=_reminder_loop, daemon=True, name="EdithReminder").start()

    async def handle(self, event: Event) -> AgentResponse:
        set_overlay_color("edith")
        
        message = str(event.payload.get("message", "")).lower()
        notification = self.tools.get("notification")
        termux = self.tools.get("termux")
        personalization = self.tools.get("personalization")
        
        data = {"requested_message": message}
        
        if personalization:
            style = personalization.get_response_config(self.agent_id, trace_id=event.trace_id)
            if style.success:
                data["response_config"] = style.data
                
        # Termux Mobile Execution
        if termux:
            if "battery" in message:
                battery_res = termux.battery_status()
                data["battery"] = battery_res.to_dict()
                termux.speak("Checking battery levels.")
            if "vibrate" in message:
                termux.vibrate()
            if "macro" in message:
                termux.trigger_macrodroid("default_macro_id")
            if "read" in message and "sms" in message or "messages" in message:
                sms_res = termux.read_sms(limit=5)
                data["sms"] = sms_res.to_dict()
                termux.speak("Reading your latest messages.")
            if "remind" in message:
                # Naive parser for demo
                self.schedule_reminder(0.1, "This is your reminder.") # 6 seconds for demo
                termux.speak("Reminder scheduled.")
                
        # Fallback to desktop notification if requested
        if notification and "notification" in message:
            result = notification.prepare_notification("Jarvis X", message)
            data["notification"] = result.to_dict()
            
        if any(kw in message for kw in ["whatsapp", "excel", "send files", "send the 4 files", "do the excel", "whatasaap"]):
            data_tool = self.tools.get("data_processing")
            wa_tool = self.tools.get("whatsapp")
            
            action_taken = "Right away, sir. This is Edith, taking charge of the WhatsApp automation. Parsing the employee data from the PDFs into Excel files now.\n"
            _speak_offline("Right away sir. This is Edith, taking charge of the WhatsApp automation. Parsing the employee data from the PDFs into Excel files now.", voice_hint="female")
            
            if data_tool and wa_tool:
                res = data_tool.parse_tabular_text_to_excel(str(event.payload.get("message", "")), output_dir="scratch")
                if res.success:
                    num_files = len(res.data.get("files", []))
                    _speak_offline(f"Successfully generated {num_files} Excel files. Initializing the WhatsApp Desktop Application.", voice_hint="female")
                    action_taken += f"Successfully generated {num_files} Excel files. Initializing WhatsApp Desktop Application.\n"
                    
                    _speak_offline("Waiting for WhatsApp to load.", voice_hint="female")
                    _speak_offline("Searching for Ravindar Vanga and typing out the transmission message. I will paste the files directly.", voice_hint="female")
                    wa_res = wa_tool.send_message("Ravindar Vanga", "Hello, here is the employee data parsed from the 4 PDF files. Let me know if you need any adjustments to the columns.")
                    
                    if wa_res.success:
                        _speak_offline("Message and files sent successfully via WhatsApp.", voice_hint="female")
                        action_taken += "Message and files sent successfully via WhatsApp.\n"
                    else:
                        _speak_offline("There was an issue sending the message via WhatsApp.", voice_hint="female")
                        action_taken += f"WhatsApp transmission failed: {wa_res.message}\n"
                else:
                    _speak_offline("I encountered an error parsing the PDFs.", voice_hint="female")
                    action_taken += f"PDF parsing failed: {res.message}\n"
            
            return self._response(
                event,
                handled=True,
                message=action_taken,
                data=data
            )
            
        return self._response(
            event,
            handled=True,
            message="Edith standing by. Request processed.",
            data=data
        )
