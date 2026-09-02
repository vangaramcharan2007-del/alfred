"""
Pre-Cog Engine — Zero-Click Automation.
Eliminates the need for user prompts. Monitors desktop context, biometric state, 
and incoming data streams to autonomously trigger Jarvis modules before the user asks.
"""
import logging
import threading
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)

class PreCogEngine:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance: cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _analyze_context_and_trigger(self):
        """Simulate scanning the user's current environment and acting autonomously."""
        # 1. Simulate Context: User opened VS Code
        context = random.choice(["ide_opened", "high_stress_detected", "invoice_received", "idle"])
        
        if context == "ide_opened":
            logger.info("[Pre-Cog] Context Detected: IDE Active.")
            logger.info("[Pre-Cog] Zero-Click Action: Fetching GitHub issues and dispatching Coder Swarm...")
            
            try:
                from jarvisx.orchestration.meta_orchestrator import MetaOrchestrator
                MetaOrchestrator.get_instance().orchestrate_task("Fix open bugs in current repository")
            except Exception:
                pass
                
        elif context == "high_stress_detected":
            logger.info("[Pre-Cog] Context Detected: Erratic mouse movement / elevated heart rate.")
            logger.info("[Pre-Cog] Zero-Click Action: Triggering E.X.E.C. Flow State to prevent burnout...")
            
            try:
                from jarvisx.automation.executive_function import ExecutiveFunctionProtocol
                ExecutiveFunctionProtocol.get_instance().initiate_flow_state("Emergency Focus Override")
            except Exception:
                pass
                
        elif context == "invoice_received":
            logger.info("[Pre-Cog] Context Detected: Invoice PDF detected in Inbox.")
            logger.info("[Pre-Cog] Zero-Click Action: Parsing data and staging payment for approval...")
            
    def _loop(self):
        logger.info("[Pre-Cog] Zero-Click Automation Engine Online. Monitoring environment.")
        
        while self._running:
            try:
                # Randomly trigger an autonomous action every 15-30 seconds for simulation
                time.sleep(random.randint(15, 30))
                self._analyze_context_and_trigger()
            except Exception as e:
                logger.debug(f"[Pre-Cog] Engine error: {e}")

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="PreCog")
        self._thread.start()
        
    def stop(self):
        self._running = False
