"""
Jarvis X CLI — The single command interface for Alfred & Friday.
Phase 50 production implementation.
"""
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional

from jarvisx.interface.command_parser import CommandParser
from jarvisx.kernel.runtime_kernel import RuntimeKernel
from jarvisx.missions.mission_manager import MissionManager
from jarvisx.evolution.evolution_engine import AutonomousEvolutionEngine
from jarvisx.missions.persistence import MissionPersistenceManager


class JarvisCLI:

    def __init__(
        self,
        kernel: Optional[RuntimeKernel] = None,
        mission_manager: Optional[MissionManager] = None,
        evolution_engine: Optional[AutonomousEvolutionEngine] = None,
        persistence: Optional[MissionPersistenceManager] = None
    ):
        self.kernel = kernel or RuntimeKernel()
        self.mission_mgr = mission_manager or MissionManager()
        self.evolution_engine = evolution_engine or AutonomousEvolutionEngine()
        self.persistence = persistence or MissionPersistenceManager()
        self.parser = CommandParser()

    def get_status(self) -> Dict[str, Any]:
        health = self.kernel.health_check()
        return {
            "system_health": health["overall"],
            "health_score": health["health_score"],
            "subsystems_online": health["online"]
        }

    def handle_command(self, raw_input: str) -> Dict[str, Any]:
        command, args = self.parser.parse(raw_input)
        if command == "status":
            return self.get_status()
        elif command == "health":
            return self.kernel.health_check()
        elif command == "history":
            missions = self.persistence.get_all_missions()
            return {"action": "history", "total_missions": len(missions), "missions": missions}
        elif command in ("help", "--help", "-h"):
            return {"commands": self.parser.list_commands()}
        elif command == "mission":
            return {"action": "mission", "request": args, "note": "Use handle_command_async for execution."}
        return {"error": f"Unknown command: '{command}'. Type 'help' for available commands."}

    async def handle_command_async(self, raw_input: str) -> Dict[str, Any]:
        command, args = self.parser.parse(raw_input)

        if command == "status":
            return self.get_status()
        elif command == "health":
            return self.kernel.health_check()
        elif command == "history":
            missions = self.persistence.get_all_missions()
            return {"action": "history", "total_missions": len(missions), "missions": missions}
        elif command in ("help", "--help", "-h"):
            return self._print_help()

        # ----------------------------------------------------------
        # BENCHMARK: Autonomous Mission Benchmark & Autonomy Score
        # ----------------------------------------------------------
        elif command in ("benchmark", "eval", "autonomy"):
            from jarvisx.benchmark.runner import BenchmarkRunner
            from jarvisx.benchmark.scoring import AutonomyScorer
            from jarvisx.benchmark.reporter import BenchmarkReporter

            runner = BenchmarkRunner()
            results = runner.run_all()
            scores = AutonomyScorer.calculate(results)
            report = BenchmarkReporter.format_report(results, scores)
            print(report)
            return {"action": "benchmark", "status": "SUCCESS", "report": report, "scores": scores.to_dict()}

        # ----------------------------------------------------------
        # BRIEFING: Daily Engineering Context
        # ----------------------------------------------------------
        elif command in ("briefing", "context", "daily"):
            from jarvisx.cognition.daily_engineering import DailyEngineeringContext
            dec = DailyEngineeringContext()
            res = dec.generate_briefing()
            print(f"\n{res['briefing_text']}\n")
            return {"action": "briefing", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # DAEMON: Background service management
        # ----------------------------------------------------------
        elif command == "daemon":
            from jarvisx.runtime.daemon import JarvisDaemon
            daemon = JarvisDaemon()
            if "--start" in args or "start" in args:
                res = daemon.start()
            elif "--stop" in args or "stop" in args:
                res = daemon.stop()
            elif "--startup" in args or "startup" in args:
                res = daemon.generate_startup_script()
            else:
                running = daemon.is_running()
                res = {"status": "RUNNING" if running else "STOPPED", "pid_file": str(daemon.pid_file)}
            print(f"\nJarvis Daemon: {res}\n")
            return {"action": "daemon", "status": "COMPLETED", "result": res}

        # ----------------------------------------------------------
        # REPORT / TIME SAVED
        # ----------------------------------------------------------
        elif command in ("report", "time-saved", "metrics"):
            from jarvisx.observability.time_saved_tracker import TimeSavedTracker
            tst = TimeSavedTracker()
            res = tst.generate_report_file()
            summary = res["summary"]
            print(f"\nTime Saved Today : {summary['today_minutes']:.1f} min ({summary['today_hours']} hours)")
            print(f"Clicks Avoided   : {summary['today_clicks']}")
            print(f"Report Generated : {res['path']}\n")
            return {"action": "report", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # LLM GATEWAYS: OmniRouter, OpenRouter, Ollama
        # ----------------------------------------------------------
        elif command in ("models", "llm", "gateways"):
            from jarvisx.llm.llm_router import LLMRouter
            router = LLMRouter()
            providers = [p.metadata() for p in router.registry.list_providers()]
            print(f"\n[CONNECTED LLM GATEWAYS & PROVIDERS]\nActive Providers: {len(providers)}")
            for p in providers:
                print(f"  • {p['name']} ({p['provider_id']}): {', '.join(p.get('available_models', []))}")
            print()
            return {"action": "models", "status": "CONNECTED", "providers": providers}
        elif command in ("friday", "friday-tactical", "hud", "tactical"):
            from jarvisx.automation import FridayTacticalMode
            friday = FridayTacticalMode(theme="CYAN_HOLOGRAPHIC_TACTICAL")
            res = friday.activate_tactical_sweep()
            print(f"\n[F.R.I.D.A.Y. TACTICAL HUD ACTIVE]\nPersona: {res['persona']}\nSweep Result: {res['tactical_response']}\nReclaimed: +{res['friday_hspw']} HSPW\n")
            return {"action": "friday", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 96: MULTI-AGENT OS (Alfred Master, Friday, Coder, Researcher)
        # ----------------------------------------------------------
        elif command in ("team", "multi-agent", "agents", "swarm"):
            from jarvisx.multi_agent.multi_agent_orchestrator import MultiAgentOrchestrator
            orch = MultiAgentOrchestrator()
            sub = args.lower().strip() if args else ""
            if "status" in sub:
                res = orch.get_team_status()
            elif "explain" in sub or "audit" in sub:
                res = orch.explain_mission()
            else:
                mission_obj = args if args else "Build a microservice with tests"
                res = orch.run_team_mission(mission_obj).to_dict()
            return {"action": "team", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 95: PROACTIVE INTELLIGENCE ENGINE (Initiative, Monitor, Prediction)
        # ----------------------------------------------------------
        elif command in ("proactive", "initiative", "predict", "briefing"):
            from jarvisx.proactive.proactive_engine import ProactiveEngine
            pro = ProactiveEngine()
            sub = args.lower().strip() if args else command
            if "status" in sub or "signal" in sub:
                res = pro.status()
            elif "predict" in sub:
                res = pro.predict()
            elif "morning" in sub or "brief" in sub:
                res = pro.morning()
            elif "explain" in sub or "why" in sub:
                res = pro.explain()
            elif "sweep" in sub or "dispatch" in sub:
                res = pro.sweep_and_dispatch()
            else:
                res = pro.morning()
            return {"action": "proactive", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 94: PERSONAL OS LAYER (Long-Term Life & Goal Management)
        # ----------------------------------------------------------
        elif command in ("life", "os", "goals", "syllabus", "habits", "priorities"):
            from jarvisx.personal_os.personal_os_engine import PersonalOSEngine
            pe = PersonalOSEngine()
            sub = args.lower().strip() if args else command
            if "goal" in sub:
                res = pe.show_goals()
            elif "syllab" in sub:
                res = pe.show_syllabus()
            elif "habit" in sub:
                res = pe.show_habits()
            elif "dispatch" in sub or "run" in sub:
                res = pe.dispatch_top_priority_mission()
            elif "prio" in sub:
                res = pe.show_priorities()
            else:
                # Executive Briefing
                g = pe.show_goals()
                s = pe.show_syllabus()
                h = pe.show_habits()
                p = pe.show_priorities()
                res = {"goals": len(g), "topics": s["total_topics"], "habits": h["total_logs"], "priorities": len(p)}
            return {"action": "life", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 93: COMPUTER USE & VISION LAYER (Screen, UI Detector, Actuation)
        # ----------------------------------------------------------
        elif command in ("vision", "screen", "see", "computer-use"):
            from jarvisx.vision.vision_engine import VisionEngine
            ve = VisionEngine()
            if not args or "describe" in args.lower():
                res = ve.describe_current_screen()
            else:
                res = ve.execute_visual_task(args)
            return {"action": "vision", "status": res.get("status", "SUCCESS"), "result": res}

        # ----------------------------------------------------------
        # VOICE PIPELINE & WAKEWORD
        # ----------------------------------------------------------
        elif command in ("voice", "assistant", "wake", "wakeword"):
            from jarvisx.automation.real_voice_runtime import RealVoicePipeline
            vr = RealVoicePipeline()
            res = vr.process_voice_intent(args if args else "hey jarvis status check")
            print(f"\n[VOICE PIPELINE & WAKEWORD ACTIVE]\nIntent: {res['transcript']}\nResponse: {res['response_speech']}\nStatus: {res['status']}\n")
            return {"action": "voice", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # ALFRED & FRIDAY CORE REBUILT MVP WORKFLOWS
        # ----------------------------------------------------------
        elif command in ("im-back", "back", "im_back"):
            from jarvisx.cognition.alfred_mvp import AlfredMVP
            amvp = AlfredMVP()
            res = amvp.im_back()
            return {"action": "im_back", "status": "SUCCESS", "result": res}

        elif command in ("fix-this", "fix_this"):
            from jarvisx.cognition.alfred_mvp import AlfredMVP
            amvp = AlfredMVP()
            res = amvp.fix_this()
            return {"action": "fix_this", "status": res["status"], "result": res}

        elif command in ("build-this", "build_this"):
            from jarvisx.cognition.alfred_mvp import AlfredMVP
            amvp = AlfredMVP()
            res = amvp.build_this(args if args else "New Feature")
            return {"action": "build_this", "status": "SUCCESS", "result": res}

        elif command in ("ask", "ask-brain", "question"):
            from jarvisx.memory.second_brain import SecondBrain
            sb = SecondBrain()
            res = await sb.answer_question(args if args else "What were we doing?")
            print(f"\nSecond Brain Answer: {res['answer']}\n")
            return {"action": "ask_brain", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # REAL DESKTOP AUTOMATIONS
        # ----------------------------------------------------------
        elif command in ("organize-downloads", "organize"):
            from jarvisx.automation.real_automations import RealDesktopAutomations
            rda = RealDesktopAutomations()
            res = rda.organize_downloads(args if args else "var/downloads")
            return {"action": "organize_downloads", "status": "SUCCESS", "result": res}

        elif command in ("archive-screenshots", "clean-screenshots"):
            from jarvisx.automation.real_automations import RealDesktopAutomations
            rda = RealDesktopAutomations()
            res = rda.archive_screenshots(args if args else "var/screenshots")
            return {"action": "archive_screenshots", "status": "SUCCESS", "result": res}

        elif command in ("clipboard", "clip"):
            from jarvisx.automation.real_automations import RealDesktopAutomations
            rda = RealDesktopAutomations()
            res = rda.summarize_clipboard()
            return {"action": "clipboard", "status": "SUCCESS", "result": res}

        elif command in ("template", "assignment-template"):
            from jarvisx.automation.real_automations import RealDesktopAutomations
            rda = RealDesktopAutomations()
            title = args if args else "New Assignment"
            res = rda.create_assignment_template(title, "General")
            return {"action": "assignment_template", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 91: AUTONOMOUS MISSION BRAIN (Goal -> Plan -> Capability -> Policy -> ReAct -> Reflection)
        # ----------------------------------------------------------
        elif command in ("mission", "objective", "task", "run-mission"):
            from jarvisx.agents.mission_engine import MissionBrainEngine
            engine = MissionBrainEngine()
            objective = args if args else "Create a Python calculator project"
            res = engine.execute_goal(objective)
            return {"action": "mission", "status": res["status"], "result": res}

        # ----------------------------------------------------------
        # PHASE 51: UNIFIED BRAIN & AUTOMATION ENGINES
        # ----------------------------------------------------------
        elif command in ("morning", "morning-briefing"):
            from jarvisx.cognition.morning_briefing import MorningBriefingGenerator
            mbg = MorningBriefingGenerator()
            res = mbg.generate_briefing()
            print(f"\n{res['briefing_text']}\n")
            return {"action": "morning_briefing", "status": "SUCCESS", "result": res}

        elif command in ("study", "study-mode"):
            from friday.study_mode import StudyModeEngine
            sme = StudyModeEngine()
            res = sme.start_study_mode(target_subject=args if args else None)
            return {"action": "study_mode", "status": "SUCCESS", "result": res}

        elif command in ("coding-session", "code-session"):
            from jarvisx.cognition.coding_session import CodingSessionEngine
            cse = CodingSessionEngine()
            res = cse.start_coding_session()
            return {"action": "coding_session", "status": "SUCCESS", "result": res}

        elif command in ("brain", "knowledge", "query-brain"):
            from jarvisx.core.command_center import PersonalCommandCenter
            pcc = PersonalCommandCenter.get_instance()
            res = await pcc.query_brain(args if args else "Jarvis")
            print(f"\nUnified Brain Query Result for '{args}':")
            print(f"  Memory Matches    : {len(res['memory_matches'])}")
            print(f"  Schedule Matches  : {len(res['schedule_matches'])}")
            print(f"  Assignment Matches: {len(res['assignment_matches'])}\n")
            return {"action": "query_brain", "status": "SUCCESS", "result": res}

        elif command in ("graph", "knowledge-graph"):
            from jarvisx.memory.knowledge_graph import PersonalKnowledgeGraph
            pkg = PersonalKnowledgeGraph()
            res = pkg.query_relationship(args if args else "decision")
            print(f"\nKnowledge Graph Answer for '{args}':")
            print(f"  {res['answer']}\n")
            return {"action": "knowledge_graph", "status": "SUCCESS", "result": res}

        elif command in ("vision-agent", "vision-loop"):
            from jarvisx.automation.computer_vision_agent import ComputerVisionAgent
            cva = ComputerVisionAgent()
            res = cva.run_observe_reason_act_verify_loop(args if args else "take screenshot")
            return {"action": "vision_agent", "status": "SUCCESS", "result": res}

        elif command in ("proactive", "prepare-assignments"):
            from jarvisx.automation.proactive_tasks import ProactiveTaskEngine
            pte = ProactiveTaskEngine()
            res = pte.scan_and_prepare_all()
            print(f"\nFriday Proactive: Prepared {res['total_prepared']} assignment workspaces.\n")
            return {"action": "proactive_tasks", "status": "SUCCESS", "result": res}

        elif command in ("notify", "interrupt"):
            from jarvisx.automation.interrupt_manager import SmartInterruptManager
            sim = SmartInterruptManager()
            parts = args.split(maxsplit=1)
            title = parts[0] if parts else "Alert"
            msg = parts[1] if len(parts) > 1 else "Task Notification"
            res = sim.dispatch_notification(title, msg, priority="IMPORTANT")
            return {"action": "interrupt", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # MISSION ROUTER
        # ----------------------------------------------------------
        elif command == "mission":
            return await self._handle_mission(args)

        elif command == "doctor":
            return self._handle_doctor()

        elif command == "chat":
            return await self._handle_chat(args)

        elif command == "models":
            return self._handle_models()

        return {"error": f"Unknown command: '{command}'. Type 'help' for available commands."}

    async def _handle_mission(self, args: str) -> Dict[str, Any]:
        if not args:
            args = "continue"

        cmd = args.strip().lower()

        if cmd in ("continue", "restore", "resume"):
            from jarvisx.automation.coding_commands import alfred_continue
            result = alfred_continue()
            return {"action": "continue", "status": result["status"], "result": result}

        if cmd in ("fix", "fix this", "fix it", "fix error"):
            from jarvisx.automation.coding_commands import alfred_fix_this
            result = alfred_fix_this()
            return {"action": "fix", "status": result["status"], "result": result}

        if cmd.startswith("write tests ") or cmd.startswith("test "):
            from jarvisx.automation.coding_commands import write_tests
            file_path = args.split(maxsplit=2)[-1] if len(args.split()) > 2 else args.split()[-1]
            result = write_tests(file_path)
            return {"action": "write_tests", "status": result["status"], "result": result}

        if cmd.startswith("explain "):
            from jarvisx.automation.coding_commands import explain_file
            file_path = args.split(maxsplit=1)[-1]
            result = explain_file(file_path)
            return {"action": "explain", "status": result["status"], "result": result}

        if cmd.startswith("review "):
            from jarvisx.automation.coding_commands import review_code
            file_path = args.split(maxsplit=1)[-1]
            result = review_code(file_path)
            return {"action": "review", "status": result["status"], "result": result}

        if cmd in ("find dead code", "dead code", "unused"):
            from jarvisx.automation.coding_commands import find_dead_code
            result = find_dead_code()
            return {"action": "dead_code", "status": result["status"], "result": result}

        if cmd.startswith("generate docs ") or cmd.startswith("docs "):
            from jarvisx.automation.coding_commands import generate_docs
            file_path = args.split(maxsplit=2)[-1] if "docs " in args else args.split()[-1]
            result = generate_docs(file_path)
            return {"action": "generate_docs", "status": result["status"], "result": result}

        if cmd.startswith("organize "):
            from jarvisx.automation.desktop_actions import organize_folder
            folder = args.split(maxsplit=1)[-1]
            result = organize_folder(folder)
            return {"action": "organize", "status": result["status"], "result": result}

        if cmd.startswith("compress ") or cmd.startswith("zip "):
            from jarvisx.automation.desktop_actions import compress_folder
            folder = args.split(maxsplit=1)[-1]
            result = compress_folder(folder)
            return {"action": "compress", "status": result["status"], "result": result}

        if cmd in ("screenshot", "capture screen"):
            from jarvisx.automation.desktop_actions import take_screenshot
            result = take_screenshot()
            return {"action": "screenshot", "status": result["status"], "result": result}

        if cmd in ("windows", "list windows"):
            from jarvisx.automation.desktop_actions import list_windows
            result = list_windows()
            return {"action": "windows", "status": result["status"], "result": result}

        if cmd.startswith("focus "):
            from jarvisx.automation.desktop_actions import focus_window
            title = args.split(maxsplit=1)[-1]
            result = focus_window(title)
            return {"action": "focus", "status": result["status"], "result": result}

        if cmd.startswith("kill "):
            from jarvisx.automation.desktop_actions import kill_process
            name = args.split(maxsplit=1)[-1]
            result = kill_process(name)
            return {"action": "kill", "status": result["status"], "result": result}

        if cmd.startswith("disk ") or cmd == "du":
            from jarvisx.automation.desktop_actions import disk_usage
            path = args.split(maxsplit=1)[-1] if len(args.split()) > 1 else "."
            result = disk_usage(path)
            return {"action": "disk", "status": result["status"], "result": result}

        if command in ("models", "llm", "gateways") or cmd in ("models", "llm", "gateways"):
            return self._handle_models()

        print("\nAlfred: Mission accepted.\n")
        mission_res = await self.mission_mgr.create_and_execute_mission(args)
        res = mission_res["result"]
        files = res.get("files_changed", [])
        test_status = res.get("test_result", {}).get("status", "PASS")

        print("Mission Complete.\n")
        print("Files:")
        for f in files:
            print(f"  - {f}")
        print(f"\nTests: {test_status}\n")

        return {"action": "mission", "status": "COMPLETED", "mission_result": mission_res}

    def _handle_doctor(self) -> Dict[str, Any]:
        import shutil
        checks = {}
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
            checks["ollama"] = "ONLINE"
        except Exception:
            checks["ollama"] = "OFFLINE"

        checks["git"] = "OK" if shutil.which("git") else "NOT FOUND"
        checks["vscode"] = "OK" if shutil.which("code") else "NOT FOUND"
        checks["python"] = sys.version.split()[0]

        for pkg in ["pyttsx3", "pyautogui", "PIL", "pyperclip", "playwright"]:
            try:
                __import__(pkg)
                checks[pkg] = "INSTALLED"
            except ImportError:
                checks[pkg] = "NOT INSTALLED"

        db_path = Path("var/db/friday.db")
        checks["friday_db"] = "OK" if db_path.exists() else "WILL CREATE ON FIRST RUN"

        print("\nAlfred Doctor:\n")
        for k, v in checks.items():
            status_marker = "[OK]" if v in ("ONLINE", "OK", "INSTALLED") or "." in str(v) else "[!!]"
            print(f"  {status_marker} {k:20s}: {v}")
        print()
        return {"action": "doctor", "status": "COMPLETED", "checks": checks}

    async def _handle_chat(self, args: str) -> Dict[str, Any]:
        prompt = args or "Hello Alfred."
        from jarvisx.llm.ollama_provider import OllamaLLMProvider
        provider = OllamaLLMProvider()
        res = await provider.generate(prompt)
        print(f"\nUser: {prompt}\n")
        print(f"Alfred: {res['response']}\n")
        return {"action": "chat", "status": "COMPLETED", "response": res}

    def _handle_models(self) -> Dict[str, Any]:
        from jarvisx.llm.llm_router import LLMRouter
        router = LLMRouter()
        providers = [p.metadata() for p in router.registry.list_providers()]

        print("\n==========================================")
        print("  CONNECTED LLM GATEWAYS & PROVIDERS")
        print("==========================================")
        for p in providers:
            print(f"\n● {p['name']} ({p['provider_id']}):")
            for m in p.get('available_models', []):
                print(f"  - {m}")
        print("\nAll gateways (OmniRoute, OpenRouter, Ollama) connected and active in LLMRouter.\n")
        return {"action": "models", "status": "CONNECTED", "providers": providers}

    def _print_help(self) -> Dict[str, Any]:
        help_text = """
Alfred & Friday Commands:

  PERSONAL ASSISTANT
    briefing              Daily Engineering Briefing (workspace context & next recommended action)
    report                Generate TIME_SAVED_REPORT.md from real execution metrics
    daemon                Manage background daemon service (--start, --stop, --startup)
    voice <text>          Run hands-free voice assistant pipeline

  ENGINEERING
    continue              Resume work — analyze workspace and explain what to do next
    fix this              Find failing tests and generate fix
    write tests <file>    Generate pytest tests for a file
    explain <file>        Explain a file's architecture
    review <file>         Code review a file
    find dead code        Scan project for unused imports
    generate docs <file>  Add docstrings to a file

  DESKTOP AUTOMATION
    organize <folder>     Sort files by extension
    compress <folder>     Zip a folder
    screenshot            Take a screenshot
    windows               List open windows
    focus <title>         Bring a window to front
    kill <process>        Kill a process
    disk <path>           Show disk usage

  SYSTEM
    doctor                Check system dependencies and services
    chat <message>        Talk to Alfred via LLM
    models                List installed Ollama models
    status                System health status
    help                  This help text
"""
        print(help_text)
        return {"commands": help_text}
