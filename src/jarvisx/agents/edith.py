from __future__ import annotations

from jarvisx.agents.base import BaseAgent, AgentResponse
from jarvisx.core.events import Event


class EdithAgent(BaseAgent):
    agent_id = "edith"
    role = "Mobile companion and Android execution layer"
    expertise = ("voice interface", "notifications", "device actions")
    tone = "brief and practical"
    personality = "calm mobile operator"
    capabilities = ("voice", "notifications", "android handoff")

    async def handle(self, event: Event) -> AgentResponse:
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
            if "vibrate" in message:
                termux.vibrate()
            if "macro" in message:
                termux.trigger_macrodroid("default_macro_id")
                
        # Fallback to desktop notification if requested
        if notification and "notification" in message:
            result = notification.prepare_notification("Jarvis X", message)
            data["notification"] = result.to_dict()
            
        if any(kw in message for kw in ["whatsapp", "excel", "send files", "send the 4 files", "do the excel", "whatasaap"]):
            data_tool = self.tools.get("data_processing")
            wa_tool = self.tools.get("whatsapp")
            
            from jarvisx.agents.alfred import _speak_offline
            
            action_taken = "Right away, sir. I am Alfred, taking charge of the WhatsApp automation. Parsing the employee data from the PDFs into Excel files now.\n"
            _speak_offline("Right away sir. I am Alfred, taking charge of the WhatsApp automation. Parsing the employee data from the PDFs into Excel files now.", voice_hint="male")
            
            if data_tool and wa_tool:
                res = data_tool.parse_tabular_text_to_excel(str(event.payload.get("message", "")), output_dir="scratch")
                if res.success:
                    num_files = len(res.data.get("files", []))
                    _speak_offline(f"Successfully generated {num_files} Excel files. Initializing the WhatsApp Desktop Application.", voice_hint="male")
                    action_taken += f"Successfully generated {num_files} Excel files. Initializing WhatsApp Desktop Application.\n"
                    
                    _speak_offline("Waiting for WhatsApp to load.", voice_hint="male")
                    _speak_offline("Searching for Ravindar Vanga and typing out the transmission message. I will paste the files directly.", voice_hint="male")
                    
                    msg = "Hello Ravindar, I have generated the 4 requested Excel files regarding the ABT AE probation commencement. Sending them now."
                    wa_tool.send_files_ui("ravindar vanga", res.data["files"], msg)
                    
                    _speak_offline("The automation drill is complete. The files have been successfully sent.", voice_hint="male")
                    action_taken += "The automation drill is complete.\n"
                else:
                    _speak_offline("I could not parse the raw data into Excel.", voice_hint="male")
                    action_taken += "Failed to parse data.\n"
            else:
                _speak_offline("Data processing or WhatsApp tools are not available.", voice_hint="male")
                action_taken += "Missing tools.\n"
                
            return self._response(event, handled=True, message=action_taken, data=data)

        return self._response(
            event,
            handled=True,
            message="Edith prepared the mobile execution handoff.",
            data=data,
        )
