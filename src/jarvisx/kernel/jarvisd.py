"""
Jarvis X Kernel Daemon (jarvisd)
The master entrypoint that boots and manages all OS subsystems.

Phase 11: Added live telemetry broadcast to E.V. UI.
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

    def _start_telemetry_broadcast(self):
        """Background thread that pushes real CPU/RAM stats to E.V. UI every 2 seconds."""
        import psutil

        def _broadcast():
            while self.running:
                try:
                    from jarvisx.dashboard.hud_server import push_event_sync
                    cpu = psutil.cpu_percent(interval=1)
                    ram = psutil.virtual_memory()
                    push_event_sync("system_stats", {
                        "cpu_percent": cpu,
                        "ram_percent": ram.percent,
                        "ram_used_gb": round(ram.used / (1024**3), 1),
                        "ram_total_gb": round(ram.total / (1024**3), 1),
                    })
                except Exception:
                    pass
                time.sleep(2)

        t = threading.Thread(target=_broadcast, daemon=True, name="TelemetryBroadcast")
        t.start()
        logger.info("-> Telemetry Broadcast ONLINE (pushing to E.V. UI every 2s)")

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

        # 3. Smart Notifier removed in Phase 17
        logger.info("-> Smart Notifier OFFLINE (Replaced by specialized agents)")

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

        # 7. Start Telemetry Broadcast to E.V. UI
        self.running = True
        self._start_telemetry_broadcast()

        # 8. Register heavy background modules with Hypervisor
        from jarvisx.automation.precog_engine import PreCogEngine
        from jarvisx.automation.executive_function import ExecutiveFunctionProtocol
        from jarvisx.vision.edith_ar import EdithAREngine
        from jarvisx.network.mcp_server import MCPServerBridge

        # ---------------------------------------------------------
        # REAL, VERIFIED AUTOMATION MODULES
        # ---------------------------------------------------------
        
        # New Real Agents
        from jarvisx.memory.chronosphere import Chronosphere
        chronosphere = Chronosphere.get_instance()
        hv.register_module("Chronosphere", chronosphere, "low")
        chronosphere.start()

        from jarvisx.memory.akashic_records import AkashicRecords
        akashic = AkashicRecords.get_instance()
        hv.register_module("AkashicRecords", akashic, "low")
        akashic.start()

        from jarvisx.finance.wall_street_swarm import WallStreetSwarm
        wallstreet = WallStreetSwarm.get_instance()
        hv.register_module("WallStreetSwarm", wallstreet, "normal")
        wallstreet.start()

        from jarvisx.engineering.devops_sentry import DevOpsSentry
        devops = DevOpsSentry.get_instance()
        hv.register_module("DevOpsSentry", devops, "normal")
        devops.start()
        
        # Graveyard Revivals
        from jarvisx.automation.reminder_engine import get_reminder_engine
        reminder = get_reminder_engine()
        hv.register_module("ReminderEngine", reminder, "normal")
        reminder.start_sentinel()

        from jarvisx.automation.system_cleaner_daemon import SystemCleanerDaemon
        cleaner_daemon = SystemCleanerDaemon.get_instance()
        hv.register_module("SystemCleaner", cleaner_daemon, "low")
        cleaner_daemon.start()

        from jarvisx.automation.system_tray_agent import SystemTrayAgent
        tray = SystemTrayAgent.get_instance()
        hv.register_module("SystemTrayAgent", tray, "normal")
        tray.start()

        # Phase 17 Active Automation Agents
        from jarvisx.automation.ghost_mail import GhostMail
        ghost_mail = GhostMail.get_instance()
        hv.register_module("GhostMail", ghost_mail, "low")
        ghost_mail.start()

        from jarvisx.automation.meeting_joiner import AutoMeetingJoiner
        meeting_joiner = AutoMeetingJoiner.get_instance()
        hv.register_module("ChronoCommute", meeting_joiner, "normal")
        meeting_joiner.start()

        from jarvisx.automation.clipboard_debugger import ClipboardDebugger
        clipboard = ClipboardDebugger.get_instance()
        hv.register_module("DebuggerSwarm", clipboard, "normal")
        clipboard.start()

        from jarvisx.automation.window_manager import WindowManagerAgent
        window_mgr = WindowManagerAgent.get_instance()
        hv.register_module("WindowManager", window_mgr, "normal")
        window_mgr.start()

        # Phase 18 Advanced AI Agents
        from jarvisx.automation.sentinel_zero import SentinelZero
        sentinel = SentinelZero.get_instance()
        hv.register_module("SentinelZero", sentinel, "critical")
        sentinel.start()

        from jarvisx.automation.athena_researcher import AthenaResearcher
        athena = AthenaResearcher.get_instance()
        hv.register_module("Athena", athena, "low")
        athena.start()

        from jarvisx.automation.davinci_vision import DaVinciVision
        davinci = DaVinciVision.get_instance()
        hv.register_module("DaVinci", davinci, "normal")
        davinci.start()

        from jarvisx.automation.midas_oracle import MidasOracle
        midas = MidasOracle.get_instance()
        hv.register_module("Midas", midas, "low")
        midas.start()

        from jarvisx.automation.zero_lag_skill_library import ZeroLagSkillLibrary
        skill_lib = ZeroLagSkillLibrary.get_instance()
        hv.register_module("SkillLibrary", skill_lib, "critical")
        # Note: We do NOT call start() with a while-loop. 0% CPU footprint.

        from jarvisx.vision.edith_ar import EdithAREngine
        hv.register_module("EdithAREngine", EdithAREngine.get_instance(), "critical")

        from jarvisx.automation.executive_function import ExecutiveFunctionProtocol
        hv.register_module("ExecutiveFunction", ExecutiveFunctionProtocol.get_instance(), "critical")

        from jarvisx.automation.precog_engine import PreCogEngine
        hv.register_module("PreCogEngine", PreCogEngine.get_instance(), "critical")

        try:
            from jarvisx.automation.ghost_browser import GhostBrowserEngine
            ghost = GhostBrowserEngine.get_instance()
            hv.register_module("GhostBrowser", ghost, "critical")
            ghost.start()
            logger.info("[GhostBrowser] Engine started")
            time.sleep(0.5)
        except ImportError:
            logger.warning("[GhostBrowser] Engine unavailable")

        from jarvisx.voice.eevee_companion import EeveeCompanion
        hv.register_module("EeveeCompanion", EeveeCompanion.get_instance(), "critical")

        # 9. Start MCP Server Bridge
        mcp = MCPServerBridge.get_instance()
        mcp.start()

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
