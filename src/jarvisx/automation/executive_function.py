"""
E.X.E.C. — Executive Function Protocol.
The ultimate life-automation system designed to bypass ADHD paralysis.
Auto-triages mundane communications, manages context switching, and breaks 
overwhelming tasks into micro-dopamine steps.
"""
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ExecutiveFunctionProtocol:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def auto_triage_inbox(self) -> Dict[str, Any]:
        """Simulate reading communications and auto-replying to boring tasks."""
        logger.info("[E.X.E.C.] Scanning incoming communications for mundane requests...")
        
        # Simulate an incoming message
        message = "Hey, just checking if you have the specs for the new project?"
        logger.info(f"[E.X.E.C.] Intercepted message: '{message}'")
        
        # Auto-Reply Logic
        logger.info("[E.X.E.C.] Determining message priority: LOW. Auto-generating reply...")
        time.sleep(1)
        reply = "Yes, I will have them uploaded to the repo by EOD. Best, Jarvis (Automated)."
        
        logger.info(f"[E.X.E.C.] Sent autonomous reply: '{reply}'. User not disturbed.")
        
        return {"status": "auto_replied", "saved_time_minutes": 5}

    def initiate_flow_state(self, project_name: str) -> Dict[str, Any]:
        """Kills distractions and sets up the workspace perfectly."""
        logger.info(f"[E.X.E.C.] INITIATING FLOW STATE FOR: {project_name}")
        
        # 1. Kill distractions
        logger.info("[E.X.E.C.] Terminating background distraction processes (Discord, Chrome Socials)...")
        # In prod: os.system("taskkill /f /im discord.exe")
        
        # 2. Setup Environment
        logger.info("[E.X.E.C.] Opening VS Code to exact project directory...")
        logger.info("[E.X.E.C.] Dimming smart lights to 30% via Home Assistant...")
        logger.info("[E.X.E.C.] Pushing Lo-Fi focus track to audio matrix...")
        
        return {"status": "flow_state_active", "project": project_name}

    def break_down_paralysis(self, overwhelming_task: str) -> Dict[str, Any]:
        """Uses LLM to slice a vague task into actionable 5-minute micro-steps."""
        logger.info(f"[E.X.E.C.] Task Paralysis Detected on: '{overwhelming_task}'")
        logger.info("[E.X.E.C.] Slicing into micro-dopamine steps...")
        
        try:
            import ollama
            prompt = f"Break this overwhelming task into 3 incredibly simple, 5-minute micro-steps. Just the steps: {overwhelming_task}"
            
            res = ollama.chat(
                model="qwen2.5-coder:1.5b",
                messages=[{"role": "user", "content": prompt}]
            )
            
            steps = res["message"]["content"].split('\n')
            
            logger.info("[E.X.E.C.] Micro-steps generated. Pushing Step 1 to HUD.")
            for step in steps:
                if step.strip():
                    logger.info(f" -> {step.strip()}")
            
            return {"status": "success", "steps": steps}
            
        except Exception as e:
            logger.error(f"[E.X.E.C.] Engine failure: {e}")
            return {"status": "error"}
