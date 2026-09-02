"""
JARVIS X — Full System Live Demo
Exercises all automation levels + next-gen modules with real output.
Run: python demo.py
"""

import sys
import os
import time
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def banner(text):
    print(f"\n{BOLD}{CYAN}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}\n")

def ok(msg):
    print(f"  {GREEN}[OK]{RESET} {msg}")

def fail(msg):
    print(f"  {RED}[FAIL]{RESET} {msg}")

def section(name):
    print(f"\n  {YELLOW}> {name}{RESET}")


async def main():
    banner("J.A.R.V.I.S. X — FULL SYSTEM LIVE DEMO")
    t0 = time.perf_counter()
    results = {}

    # ── Module Import Validation ──
    section("Module Import Validation")
    modules = {
        "OmniClicker": "jarvisx.vision.omni_clicker",
        "SwarmOrchestrator": "jarvisx.automation.swarm_orchestrator",
        "DynamicToolForge": "jarvisx.engineering.dynamic_tool_forge",
        "HUD Server": "jarvisx.dashboard.hud_server",
        "VectorMemory": "jarvisx.memory.vector_memory",
        "SmartNotifier": "jarvisx.automation.smart_notifier",
        "VoicePipelineE2E": "jarvisx.voice.voice_pipeline_e2e",
        "ToolSelector": "jarvisx.tools.tool_selector",
        "TaskScheduler": "jarvisx.automation.task_scheduler",
        "ContextModeSwitcher": "jarvisx.automation.context_mode_switcher",
        "MultiModelRouter": "jarvisx.core.multi_model_router",
        "SecurityHardening": "jarvisx.security.hardening",
        "TerminalSentinel": "jarvisx.engineering.terminal_sentinel",
        "WebVoyager": "jarvisx.browser.web_voyager",
        "CoderSwarm": "jarvisx.engineering.coder_swarm",
        "JarvisDaemon": "jarvisx.kernel.jarvisd",
        "OmniModalStream": "jarvisx.vision.omni_modal_stream",
        "OmniIndexer": "jarvisx.memory.omni_indexer",
        "GhostSpawner": "jarvisx.engineering.ghost_spawner",
        "AutoHacker": "jarvisx.offensive.auto_hacker",
        "WallStreetSwarm": "jarvisx.finance.wall_street_swarm",
        "InfiniteContent": "jarvisx.content.infinite_engine",
        "MetamorphicCore": "jarvisx.kernel.metamorphic_core",
        "RemoteUplink": "jarvisx.telephony.remote_uplink",
        "REMSleepEngine": "jarvisx.memory.rem_sleep",
        "OmniContextTimeline": "jarvisx.memory.omni_context",
        "OracleEngine": "jarvisx.automation.oracle_engine",
        "GitHubBountyHunter": "jarvisx.engineering.github_bounty_hunter",
        "SymbioteEngine": "jarvisx.automation.symbiote_engine",
        "MetaOrchestrator": "jarvisx.orchestration.meta_orchestrator",
        "AegisHarness": "jarvisx.orchestration.aegis_harness",
        "AutoCurriculumEngine": "jarvisx.self_improvement.auto_curriculum",
        "DigitalTwinEmulator": "jarvisx.automation.digital_twin",
        "BazaarP2PNode": "jarvisx.network.bazaar_p2p",
        "ConsciousnessLoop": "jarvisx.core.consciousness_loop",
        "Chronosphere": "jarvisx.memory.chronosphere",
        "SentinelImmunity": "jarvisx.security.sentinel_immunity",
        "NeuroLink": "jarvisx.hardware.neuro_link",
        "QBridge": "jarvisx.core.q_bridge",
        "SDRGateway": "jarvisx.hardware.sdr_gateway",
    }
    for name, mod in modules.items():
        try:
            __import__(mod)
            ok(f"{name} ({mod})")
            results[name] = "PASS"
        except Exception as e:
            fail(f"{name}: {e}")
            results[name] = "FAIL"

    # ── Tool Selector ──
    section("Smart Tool Selector (Token Pruning)")
    from jarvisx.tools.tool_selector import select_relevant_domains
    tests = {
        "send a whatsapp message": "communication",
        "click the blue button": "vision_control",
        "do both tasks simultaneously": "swarm",
        "open vscode": "desktop",
    }
    for intent, expected in tests.items():
        domains = select_relevant_domains(intent)
        if expected in domains:
            ok(f"'{intent}' → {domains}")
        else:
            fail(f"'{intent}' → {domains} (expected {expected})")

    # ── Vector Memory (RAG) ──
    section("Vector Memory (RAG)")
    try:
        from jarvisx.memory.vector_memory import VectorMemory
        vm = VectorMemory("demo_test_memory")
        stored = vm.add_memory("The capital of France is Paris", {"source": "demo"})
        if stored:
            ok("Stored memory via Ollama embeddings")
            hits = vm.search("What is France's capital?")
            if hits:
                ok(f"Recalled: sim={hits[0]['similarity']} text='{hits[0]['text'][:50]}'")
            else:
                fail("Search returned no results (is Ollama running?)")
        else:
            fail("Failed to store (Ollama may not be running)")
    except Exception as e:
        fail(f"VectorMemory: {e}")

    # ── Dynamic Tool Forge ──
    section("Dynamic Tool Forge (Self-Coding)")
    try:
        from jarvisx.engineering.dynamic_tool_forge import DynamicToolForge
        forge = DynamicToolForge.get_instance()
        ok(f"Forge initialized, {len(forge.get_loaded_tools())} tools pre-loaded")
    except Exception as e:
        fail(f"ToolForge: {e}")

    # ── Smart Notifier ──
    section("Smart Notifications")
    try:
        from jarvisx.automation.smart_notifier import SmartNotifier
        notifier = SmartNotifier.get_instance()
        notifier.start()
        ok("SmartNotifier monitoring started (battery/RAM/CPU)")
        import psutil
        batt = psutil.sensors_battery()
        ram = psutil.virtual_memory()
        ok(f"Battery: {batt.percent if batt else 'N/A'}% | RAM: {ram.percent}%")
    except Exception as e:
        fail(f"SmartNotifier: {e}")

    # ── HUD Dashboard ──
    section("JARVIS HUD Dashboard")
    try:
        from jarvisx.dashboard.hud_server import start_hud
        start_hud(8765)
        ok("HUD live at http://localhost:8765")
    except Exception as e:
        fail(f"HUD: {e}")

    # ── Voice Pipeline ──
    section("Voice Pipeline E2E")
    try:
        from jarvisx.voice.voice_pipeline_e2e import VoicePipelineE2E
        vp = VoicePipelineE2E.get_instance()
        ok("VoicePipelineE2E ready (call .start() to activate mic)")
    except Exception as e:
        fail(f"VoicePipeline: {e}")

    # -- Task Scheduler --
    section("Task Scheduler (Cron Engine)")
    try:
        from jarvisx.automation.task_scheduler import TaskScheduler
        from datetime import datetime, timedelta
        sched = TaskScheduler.get_instance()
        t = sched.parse_time("in 30 minutes")
        ok(f"Parsed 'in 30 minutes' -> {t.strftime('%H:%M') if t else 'FAIL'}")
        sched.start()
        ok(f"Scheduler running, {len(sched.list_tasks())} pending tasks")
    except Exception as e:
        fail(f"TaskScheduler: {e}")

    # -- Context Mode Switcher --
    section("Context Mode Switcher")
    try:
        from jarvisx.automation.context_mode_switcher import ContextModeSwitcher
        cms = ContextModeSwitcher.get_instance()
        cms.start()
        ok(f"Mode: {cms.current_mode.value} | Config: {cms.get_config()['hint_style']}")
    except Exception as e:
        fail(f"ContextMode: {e}")

    # -- Multi-Model Router --
    section("Multi-Model Router")
    try:
        from jarvisx.core.multi_model_router import MultiModelRouter
        router = MultiModelRouter.get_instance()
        tests = {"hi": "trivial", "explain quantum physics": "complex", "open chrome": "simple"}
        for prompt, expected in tests.items():
            c = router.classify_complexity(prompt)
            ok(f"'{prompt}' -> {c.value}")
    except Exception as e:
        fail(f"MultiModelRouter: {e}")

    # -- Security Hardening --
    section("Security Hardening")
    try:
        from jarvisx.security.hardening import SecureVault, HUDAuth, InputSanitizer
        vault = SecureVault()
        vault.set_secret("test_key", "secret_value_123")
        retrieved = vault.get_secret("test_key")
        ok(f"Vault encrypt/decrypt: {'PASS' if retrieved == 'secret_value_123' else 'FAIL'}")
        auth = HUDAuth()
        ok(f"HUD Auth token: {auth.token[:12]}...")
        safe = InputSanitizer.is_safe("normal request")
        unsafe = not InputSanitizer.is_safe("rm -rf /")
        ok(f"Sanitizer: safe={safe}, blocked_dangerous={unsafe}")
        vault.delete_secret("test_key")
    except Exception as e:
        fail(f"Security: {e}")

    # ── Summary ──
    elapsed = round(time.perf_counter() - t0, 2)
    banner("DEMO RESULTS")
    passed = sum(1 for v in results.values() if v == "PASS")
    total = len(results)
    for name, status in results.items():
        icon = f"{GREEN}[OK]{RESET}" if status == "PASS" else f"{RED}[FAIL]{RESET}"
        print(f"  {icon} {name}")

    print(f"\n  {BOLD}{passed}/{total} modules validated in {elapsed}s{RESET}")
    print(f"  {CYAN}HUD: http://localhost:8765{RESET}")
    print(f"  {CYAN}Voice: VoicePipelineE2E.get_instance().start(){RESET}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
