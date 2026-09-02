"""
Jarvis X Kernel Daemon (jarvisd)
The master entrypoint that boots and manages all OS subsystems.
"""
import sys
import time
import logging
import threading
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("jarvisd")

# Ensure imports work when run as script
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class JarvisDaemon:
    def __init__(self):
        self.running = False
        
    def boot(self):
        logger.info("==========================================")
        logger.info("   BOOTING JARVIS X OS KERNEL (jarvisd)   ")
        logger.info("==========================================")
        
        # 1. Start Task Scheduler
        from jarvisx.automation.task_scheduler import TaskScheduler
        TaskScheduler.get_instance().start()
        logger.info("-> Task Scheduler ONLINE")
        
        # 2. Start Context Mode Switcher
        from jarvisx.automation.context_mode_switcher import ContextModeSwitcher
        ContextModeSwitcher.get_instance().start()
        logger.info("-> Context Mode Switcher ONLINE")
        
        # 3. Start Smart Notifier
        from jarvisx.automation.smart_notifier import SmartNotifier
        SmartNotifier.get_instance().start()
        logger.info("-> Smart Notifier ONLINE")
        
        # 4. Start HUD Server
        from jarvisx.dashboard.hud_server import start_hud
        start_hud(8765)
        logger.info("-> HUD Server ONLINE (http://localhost:8765)")
        
        # 5. Start Voice Pipeline
        from jarvisx.voice.voice_pipeline_e2e import VoicePipelineE2E
        vp = VoicePipelineE2E.get_instance()
        vp.start()
        logger.info("-> Voice Pipeline E2E ONLINE")
        
        # 6. Start Hypervisor (Resource Governor)
        from jarvisx.kernel.hypervisor import Hypervisor
        hv = Hypervisor.get_instance()
        hv.start()
        logger.info("-> Hypervisor (Resource Governor) ONLINE")
        
        # 7. Register heavy background modules with Hypervisor
        from jarvisx.memory.omni_indexer import OmniIndexer
        from jarvisx.core.consciousness_loop import ConsciousnessLoop
        from jarvisx.memory.chronosphere import Chronosphere
        from jarvisx.automation.oracle_engine import OracleEngine
        from jarvisx.automation.symbiote_engine import SymbioteEngine
        
        hv.register_module("OmniIndexer", OmniIndexer.get_instance(), "low")
        hv.register_module("Chronosphere", Chronosphere.get_instance(), "low")
        hv.register_module("ConsciousnessLoop", ConsciousnessLoop.get_instance(), "normal")
        hv.register_module("OracleEngine", OracleEngine.get_instance(), "normal")
        hv.register_module("SymbioteEngine", SymbioteEngine.get_instance(), "normal")
        
        self.running = True
        logger.info("==========================================")
        logger.info("         ALL SYSTEMS GREEN                ")
        logger.info("==========================================")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
            
    def shutdown(self):
        logger.info("Shutting down Jarvis X OS...")
        self.running = False

if __name__ == "__main__":
    daemon = JarvisDaemon()
    daemon.boot()
