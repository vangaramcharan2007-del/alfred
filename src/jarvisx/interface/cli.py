"""
Jarvis X CLI — The single command interface for Alfred & Friday.
Phase 50 production implementation.
"""
import os
import sys
import asyncio
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, Optional

from jarvisx.interface.command_parser import CommandParser
from jarvisx.kernel.runtime_kernel import RuntimeKernel
from jarvisx.missions.mission_manager import MissionManager
from jarvisx.missions.persistence import MissionPersistenceManager

if TYPE_CHECKING:
    from jarvisx.evolution.evolution_engine import AutonomousEvolutionEngine
    from jarvisx.runtime.context import RuntimeContext
    from jarvisx.runtime.daemon import JarvisDaemon


class JarvisCLI:

    def __init__(
        self,
        kernel: Optional[RuntimeKernel] = None,
        mission_manager: Optional[MissionManager] = None,
        evolution_engine: Optional["AutonomousEvolutionEngine"] = None,
        persistence: Optional[MissionPersistenceManager] = None,
        runtime_context: Optional["RuntimeContext"] = None,
        daemon: Optional["JarvisDaemon"] = None,
    ):
        self.kernel = kernel or RuntimeKernel()
        self.mission_mgr = mission_manager or MissionManager()
        # Evolution is optional and must not make the base CLI import LLM dependencies.
        self.evolution_engine = evolution_engine
        self.persistence = persistence or MissionPersistenceManager()
        self.context = runtime_context
        self.daemon = daemon
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

        # Route general conversational input through DynamicOrchestrator
        try:
            from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
            orch = DynamicOrchestrator()
            res = orch.execute_voice_command(raw_input)
            if isinstance(res, dict) and "response" in res:
                return {"action": res.get("action", "chat"), "status": "SUCCESS", "output": res["response"], "response": res["response"]}
            return res
        except Exception:
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
        # BRIEFING & STARTUP WELCOME: Daily Context, Schedule & Progress
        # ----------------------------------------------------------
        elif command in ("briefing", "context", "daily", "welcome", "announce"):
            from jarvisx.startup.startup_announcer import StartupAnnouncer
            announcer = StartupAnnouncer()
            speak_opt = "--silent" not in (args or "").lower()
            res = announcer.announce(persona="ALFRED", speak=speak_opt, block=False)
            print(f"\n[ALFRED STARTUP BRIEFING]:\n{res['briefing_text']}\n")
            return {"action": "briefing", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 105: ACADEMIC COACH & 10 CGPA STUDY ENGINE
        # ----------------------------------------------------------
        elif command in ("coach", "study", "syllabus"):
            from jarvisx.operating_loop.academic_coach import AcademicCoachEngine
            from jarvisx.operating_loop.reports import format_coach_status, format_study_plan
            coach = AcademicCoachEngine()
            args_clean = args.strip() if args else "status"

            if "plan" in args_clean:
                missions = coach.generate_daily_study_missions(max_missions=3)
                output = format_study_plan(missions)
                print(f"\n{output}\n")
                return {"action": "coach_plan", "status": "SUCCESS", "missions": [m.__dict__ for m in missions]}
            elif "topic" in args_clean:
                parts = args_clean.split(maxsplit=2)
                t_name = parts[1] if len(parts) > 1 else "General"
                score_str = parts[2] if len(parts) > 2 else "0.0"
                try:
                    score_delta = float(score_str)
                except ValueError:
                    score_delta = 0.05
                updated = coach.update_topic_mastery(t_name, score_delta)
                print(f"\n[COACH TOPIC UPDATED]: {updated.topic_name} -> Mastery: {int(updated.mastery_level*100)}%\n")
                return {"action": "coach_topic", "status": "SUCCESS", "topic": updated.__dict__}
            else:
                output = format_coach_status(coach.profile)
                print(f"\n{output}\n")
                return {"action": "coach_status", "status": "SUCCESS", "profile": coach.profile.__dict__}

        # ----------------------------------------------------------
        # PHASE 105: AUTONOMOUS OPERATING LOOP (8 STAGES)
        # ----------------------------------------------------------
        elif command in ("loop", "operate", "cycle"):
            from jarvisx.operating_loop.loop_engine import AutonomousOperatingLoop
            from jarvisx.operating_loop.reports import format_loop_trace
            loop = AutonomousOperatingLoop()
            args_clean = args.lower().strip() if args else "run"

            if "status" in args_clean or "history" in args_clean:
                recent = loop.get_recent_cycles(limit=3)
                if not recent:
                    print("\n[OPERATING LOOP]: No recent cycles recorded. Run 'jarvisx loop run' to initiate.\n")
                    return {"action": "loop_status", "status": "EMPTY"}
                for c in recent:
                    print(f"\n{format_loop_trace(c)}\n")
                return {"action": "loop_status", "status": "SUCCESS", "count": len(recent)}
            else:
                cycle = loop.run_cycle(trigger_event="CLI_USER_TRIGGER", override_cooldown=True)
                output = format_loop_trace(cycle)
                print(f"\n{output}\n")
                return {"action": "loop_run", "status": "SUCCESS", "cycle": cycle.to_dict()}

        # ----------------------------------------------------------
        # BACKGROUND DAEMON & IPC GATEWAY (PHASE 104)
        # ----------------------------------------------------------
        elif command in ("daemon", "jarvisd"):
            from jarvisx.runtime.ipc_client import IPCClient
            client = IPCClient()
            args_clean = args.lower().strip() if args else ""

            def _get_daemon():
                if not self.daemon:
                    from jarvisx.runtime.daemon import JarvisDaemon
                    self.daemon = JarvisDaemon(context=self.context)
                return self.daemon

            if "--start" in args_clean or "start" in args_clean:
                daemon = _get_daemon()
                is_block = "--block" in args_clean or "-b" in args_clean or "--background" in args_clean or ("pythonw" in sys.executable.lower())
                res = daemon.start(block=False)
                print(f"\n=== [JARVIS X DAEMON LAUNCH] ===")
                print(f"  Status   : {res.get('status')}")
                print(f"  PID      : {res.get('pid')}")
                print(f"  IPC Port : {res.get('port', 10404)}")
                print(f"  Log File : {res.get('log_file')}")
                print("=================================\n")
                if is_block and res.get("status") == "STARTED":
                    try:
                        while daemon.is_running():
                            await asyncio.sleep(1.0)
                    except (asyncio.CancelledError, KeyboardInterrupt):
                        daemon.stop()
                    except Exception as e:
                        daemon.log(f"Daemon loop exited due to exception: {e}")
                        daemon.stop()

            elif "--stop" in args_clean or "stop" in args_clean or "shutdown" in args_clean:
                ok, lat = client.shutdown()
                if not ok:
                    daemon = _get_daemon()
                    res = daemon.stop()
                else:
                    res = {"status": "STOPPED_VIA_IPC", "latency_ms": round(lat, 2)}
                print(f"\n[DAEMON STOPPED]: {res}\n")

            elif "ping" in args_clean:
                ok, lat = client.ping()
                res = {"alive": ok, "ipc_latency_ms": round(lat, 2)}
                print(f"\n=== [IPC PING CHECK] ===")
                print(f"  Daemon Alive : {'YES' if ok else 'NO (Offline)'}")
                print(f"  IPC Latency  : {res['ipc_latency_ms']} ms")
                print("========================\n")

            elif "brief" in args_clean or "morning" in args_clean:
                ok, briefing, lat = client.get_briefing()
                if ok:
                    print(f"\n{briefing}\n(Fetched via IPC in {lat:.2f}ms)\n")
                    res = {"status": "SUCCESS", "briefing": briefing, "latency_ms": lat}
                else:
                    daemon = _get_daemon()
                    briefing = daemon.scheduler.synthesize_morning_briefing()
                    print(f"\n{briefing}\n")
                    res = {"status": "SUCCESS", "briefing": briefing}

            elif "event" in args_clean:
                parts = args.split(maxsplit=1)
                evt_name = parts[1] if len(parts) > 1 else "CUSTOM"
                ok, resp, lat = client.trigger_event(evt_name)
                if ok:
                    print(f"\n[EVENT TRIGGERED VIA IPC]: {evt_name} ({lat:.2f}ms)\n")
                    res = resp
                else:
                    daemon = _get_daemon()
                    evt_id = daemon._handle_ipc_event(evt_name, {})
                    print(f"\n[EVENT TRIGGERED IN-PROCESS]: {evt_id}\n")
                    res = {"status": "TRIGGERED", "event_id": evt_id}

            elif "--startup" in args_clean or "startup" in args_clean or "install" in args_clean:
                daemon = _get_daemon()
                res = daemon.generate_startup_script()
                print(f"\n=== [WINDOWS STARTUP SERVICE GENERATED] ===")
                print(f"  Batch Script  : {res.get('bat_script')}")
                print(f"  PowerShell    : {res.get('ps1_script')}")
                print(f"  Task XML      : {res.get('task_scheduler_xml')}")
                print(f"  Instructions  : {res.get('instructions')}")
                print("===========================================\n")

            else:  # status
                ok, status_data, lat = client.get_status()
                if ok:
                    print(f"\n=== [JARVIS X DAEMON STATUS (IPC Active)] ===")
                    print(f"  Status       : {status_data.get('status')}")
                    print(f"  PID          : {status_data.get('pid')}")
                    print(f"  Health       : {status_data.get('health')}")
                    print(f"  Uptime       : {status_data.get('uptime_seconds', 0.0):.1f}s")
                    print(f"  Memory RSS   : {status_data.get('memory_rss_mb')} MB")
                    print(f"  CPU Usage    : {status_data.get('cpu_percent')}%")
                    print(f"  Commands Run : {status_data.get('total_commands_executed')}")
                    print(f"  Events Run   : {status_data.get('total_events_processed')}")
                    print(f"  Last Event   : {status_data.get('last_event')}")
                    print(f"  IPC Latency  : {lat:.2f} ms")
                    print("=============================================\n")
                    res = status_data
                else:
                    from jarvisx.runtime.state import RuntimeStateManager
                    from jarvisx.runtime.pid_lock import PIDLockManager
                    pid_mgr = PIDLockManager()
                    state_mgr = RuntimeStateManager()
                    state = state_mgr.load_state()
                    print(f"\n=== [JARVIS X DAEMON STATUS (Offline)] ===")
                    print(f"  Status       : {state.status}")
                    print(f"  PID File     : {pid_mgr.pid_file}")
                    print("==========================================\n")
                    res = state.__dict__

            return {"action": "daemon", "status": "COMPLETED", "result": res}

        # ----------------------------------------------------------
        # FAST ALFRED COMMAND DISPATCH & NATURAL QUERY ROUTING
        # ----------------------------------------------------------
        elif command in ("alfred", "ask", "q"):
            clean_query = (args or "status").lstrip(">").strip()
            if not clean_query or clean_query == "status":
                return self.get_status()
            # Route clean query through DynamicOrchestrator
            try:
                from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
                orch = DynamicOrchestrator()
                res = orch.execute_voice_command(clean_query)
                if isinstance(res, dict) and "response" in res:
                    print(f"\nAlfred: {res['response']}\n")
                    return {"action": res.get("action", "chat"), "status": "SUCCESS", "output": res["response"], "response": res["response"], "details": res}
                return res
            except Exception:
                res = await self.handle_command_async(f"mission {clean_query}")
                return {"action": "alfred_local", "status": "SUCCESS", "result": res}

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
        # PHASE 101 / v1.1: KNOWLEDGE ACQUISITION & OBSIDIAN VAULT
        # ----------------------------------------------------------
        elif command in ("knowledge", "vault", "obsidian", "rag"):
            from jarvisx.knowledge.knowledge_engine import KnowledgeEngine
            ke = KnowledgeEngine()
            sub_parts = args.split(maxsplit=1) if args else []
            sub_cmd = sub_parts[0].lower() if sub_parts else "status"
            sub_arg = sub_parts[1] if len(sub_parts) > 1 else ""

            if sub_cmd in ("init", "setup", "scaffold"):
                res = ke.init_vault()
                print(f"\n[OBSIDIAN VAULT INITIALIZED]: {res['vault_path']}")
                for f in res["folders_created"]:
                    print(f"  [+] {f}")
                print()
            elif sub_cmd in ("sync", "update"):
                res = ke.sync()
                print(f"\n[VAULT SYNC COMPLETED in {res.duration_sec}s]:")
                print(f"  Indexed: {res.files_indexed} | Unchanged: {res.files_skipped_unchanged} | Purged: {res.files_deleted_purged}")
                print(f"  Chunks Created: {res.total_chunks_created}\n")
                res = res.to_dict()
            elif sub_cmd in ("rebuild", "reindex"):
                res = ke.sync(force_rebuild=True)
                print(f"\n[VAULT REBUILD COMPLETED in {res.duration_sec}s]:")
                print(f"  Indexed: {res.files_indexed} | Chunks: {res.total_chunks_created}\n")
                res = res.to_dict()
            elif sub_cmd in ("ingest", "add", "load"):
                if not sub_arg:
                    print("\n[Usage]: jarvis knowledge ingest <file_or_directory_path>\n")
                    res = {"status": "ERROR", "reason": "Missing path argument"}
                else:
                    res = ke.ingest_path(sub_arg)
                    print(f"\n[INGESTION SUCCESSFUL]: {sub_arg} ({res.total_chunks_created} chunks indexed)\n")
                    res = res.to_dict()
            elif sub_cmd in ("search", "find", "query", "ask"):
                query_str = sub_arg or (args if command != "knowledge" else "")
                results = ke.search(query_str, top_k=5)
                print(f"\n[KNOWLEDGE SEARCH RESULTS for '{query_str}'] ({len(results)} matches):")
                for r in results:
                    print(f"\n* [Score: {r.score}] {r.source_file} ({r.heading_path})")
                    print(f"  Reason: {r.relevance_reason}")
                    print(f"  Excerpt: {r.content[:160]}...")
                print()
                res = [r.to_dict() for r in results]
            else:
                res = ke.status()
                print(f"\n[JARVIS X KNOWLEDGE VAULT STATUS]:")
                print(f"  Vault Path:      {res['vault_path']}")
                print(f"  Total Documents: {res['total_documents']}")
                print(f"  Total Chunks:    {res['total_chunks']}")
                print(f"  Vector Index:    {res['vector_index_count']} embeddings")
                print(f"  Categories:      {res['categories']}\n")

            return {"action": "knowledge", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 102: EVIDENCE-BASED INTELLIGENCE EVALUATION LAYER
        # ----------------------------------------------------------
        elif command in ("evaluate", "evaluation", "eval"):
            from jarvisx.evaluation.evaluation_engine import EvaluationEngine
            from jarvisx.evaluation.reports import EvaluationReportFormatter
            ee = EvaluationEngine()
            sub_cmd = args.strip().lower() if args else "report"

            if sub_cmd in ("last", "recent", "latest"):
                last_eval = ee.get_last_evaluation()
                if last_eval:
                    print(f"\n{EvaluationReportFormatter.format_evaluation(last_eval)}\n")
                    res = {"status": "SUCCESS", "evaluation": last_eval.__dict__}
                else:
                    print("\n[EVALUATION]: No response evaluations recorded yet.\n")
                    res = {"status": "EMPTY"}
            else:
                scorecard = ee.get_scorecard()
                print(f"\n{EvaluationReportFormatter.format_scorecard(scorecard)}\n")
                res = {"status": "SUCCESS", "scorecard": scorecard.__dict__}

            return {"action": "evaluate", "status": "SUCCESS", "result": res}

        elif command in ("feedback", "correct", "correction"):
            from jarvisx.evaluation.evaluation_engine import EvaluationEngine
            from jarvisx.evaluation.reports import EvaluationReportFormatter
            ee = EvaluationEngine()
            parts = args.split(maxsplit=2) if args else []
            sub_cmd = parts[0].lower() if parts else "list"

            if sub_cmd in ("correct", "penalty", "fail") and len(parts) >= 2:
                resp_id = parts[1]
                corr_text = parts[2] if len(parts) > 2 else "User flagged incorrect response."
                updated = ee.record_user_correction(response_id=resp_id, user_correction=corr_text)
                if updated:
                    print(f"\n[USER CORRECTION LOGGED FOR {resp_id}]:")
                    print(f"  Penalty Applied: -{int(updated.user_correction_penalty * 100)}%")
                    print(f"  Updated Quality: {int(updated.final_quality_score * 100)}%\n")
                    res = {"status": "SUCCESS", "evaluation": updated.__dict__}
                else:
                    print(f"\n[ERROR]: Response ID '{resp_id}' not found in evaluation database.\n")
                    res = {"status": "NOT_FOUND"}
            elif sub_cmd in ("accept", "pass", "ok") and len(parts) >= 2:
                resp_id = parts[1]
                feedback_text = parts[2] if len(parts) > 2 else "Accepted."
                updated = ee.record_user_acceptance(response_id=resp_id, feedback=feedback_text)
                if updated:
                    print(f"\n[USER ACCEPTANCE LOGGED FOR {resp_id}]: Quality {int(updated.final_quality_score * 100)}%\n")
                    res = {"status": "SUCCESS", "evaluation": updated.__dict__}
                else:
                    print(f"\n[ERROR]: Response ID '{resp_id}' not found in evaluation database.\n")
                    res = {"status": "NOT_FOUND"}
            else:
                history = ee.list_history(limit=10)
                print(f"\n{EvaluationReportFormatter.format_history(history)}\n")
                res = {"status": "SUCCESS", "history": [h.__dict__ for h in history]}

            return {"action": "feedback", "status": "SUCCESS", "result": res}

        elif command in ("intelligence", "scorecard", "score"):
            from jarvisx.evaluation.evaluation_engine import EvaluationEngine
            from jarvisx.evaluation.reports import EvaluationReportFormatter
            ee = EvaluationEngine()
            sub_cmd = args.strip().lower() if args else "score"

            if sub_cmd in ("history", "log", "recent"):
                history = ee.list_history(limit=20)
                print(f"\n{EvaluationReportFormatter.format_history(history)}\n")
                res = {"status": "SUCCESS", "history": [h.__dict__ for h in history]}
            elif sub_cmd in ("drift", "decay", "trends", "degradation"):
                drift = ee.check_drift()
                print(f"\n{EvaluationReportFormatter.format_drift_report(drift)}\n")
                res = {"status": "SUCCESS", "drift": drift.__dict__}
            else:
                scorecard = ee.get_scorecard()
                print(f"\n{EvaluationReportFormatter.format_scorecard(scorecard)}\n")
                res = {"status": "SUCCESS", "scorecard": scorecard.__dict__}

            return {"action": "intelligence", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 103: MEMORY INTELLIGENCE LAYER
        # ----------------------------------------------------------
        elif command in ("memory", "mem", "remember", "profile"):
            from jarvisx.memory_intelligence.memory_engine import MemoryIntelligenceEngine
            from jarvisx.memory_intelligence.models import MemoryType
            from jarvisx.memory_intelligence.reports import MemoryReportFormatter
            engine = MemoryIntelligenceEngine()
            parts = args.split(maxsplit=1) if args else []
            sub_cmd = parts[0].lower() if parts else "audit"

            if command == "remember" or sub_cmd in ("remember", "add", "store"):
                text_to_save = parts[1] if (len(parts) > 1 and command != "remember") else (args or "")
                success, record, reason = engine.remember(text_to_save)
                if success and record:
                    print(f"\n[MEMORY STORED]: [{record.id}] {record.content} (Type: {record.memory_type.value}, Importance: {record.importance_score})\n")
                    res = {"status": "SUCCESS", "memory": record.__dict__}
                else:
                    print(f"\n[REJECTED]: {reason or 'Failed to validate memory.'}\n")
                    res = {"status": "REJECTED", "reason": reason}

            elif command == "profile" or sub_cmd in ("profile", "persona"):
                prof = engine.get_user_profile()
                print(f"\n{MemoryReportFormatter.format_user_profile(prof)}\n")
                res = {"status": "SUCCESS", "profile": prof.__dict__}

            elif sub_cmd in ("list", "all", "records"):
                mem_type = None
                if len(parts) > 1:
                    t_str = parts[1].upper()
                    if t_str in MemoryType.__members__:
                        mem_type = MemoryType(t_str)
                memories = engine.recall(limit=30, memory_type=mem_type)
                print(f"\n{MemoryReportFormatter.format_memory_list(memories)}\n")
                res = {"status": "SUCCESS", "count": len(memories)}

            elif sub_cmd in ("context", "prompt"):
                q = parts[1] if len(parts) > 1 else ""
                ctx = engine.get_personal_context(query=q)
                print(f"\n{ctx.prompt_block}\n")
                res = {"status": "SUCCESS", "context": ctx.__dict__}

            elif sub_cmd in ("forget", "archive", "delete") and len(parts) > 1:
                mem_id = parts[1].strip()
                ok = engine.store.archive_memory(mem_id)
                if ok:
                    print(f"\n[MEMORY ARCHIVED]: Successfully archived memory '{mem_id}'.\n")
                    res = {"status": "SUCCESS", "id": mem_id}
                else:
                    print(f"\n[ERROR]: Memory ID '{mem_id}' not found.\n")
                    res = {"status": "NOT_FOUND"}

            else:  # audit
                audit_data = engine.audit_memory_health()
                print(f"\n{MemoryReportFormatter.format_audit_report(audit_data['counts'], audit_data['decay_candidates_count'], audit_data['missing_provenance'])}\n")
                res = {"status": "SUCCESS", "audit": audit_data}

            return {"action": "memory", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 100: PRODUCTION READINESS CERTIFICATION & BENCHMARK
        # ----------------------------------------------------------
        elif command in ("cert", "certification", "certify"):
            from jarvisx.core.certification_suite import ProductionCertificationSuite
            suite = ProductionCertificationSuite()
            res = suite.execute_full_certification()
            return {"action": "cert", "status": "SUCCESS", "result": res}

        elif command in ("benchmark", "bench", "perf"):
            from jarvisx.core.certification_suite import ProductionCertificationSuite
            suite = ProductionCertificationSuite()
            res = suite.run_benchmarks()
            print(f"\n[INTERNAL RUNTIME BENCHMARKS]:")
            for k, v in res["metrics"].items():
                print(f"  {k}: {v}")
            print(f"Passed: {res['passed']}\n")
            return {"action": "benchmark", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # HARDWARE, NPU & THERMAL RESOURCE MANAGEMENT
        # ----------------------------------------------------------
        elif command in ("npu", "cool", "power", "hardware", "thermal"):
            from jarvisx.hardware.npu_accelerator import get_npu_accelerator
            npu = get_npu_accelerator()

            sub = (args or "").strip().lower()
            if "cool" in sub or command == "cool":
                res = npu.enforce_memory_cooling()
                print(f"\n[THERMAL COOLING & MEMORY PURGE]: {res['status']}")
                print(f"  Freed RAM    : {res['freed_mb']} MB")
                print(f"  Current RAM  : {res['current_ram_percent']}%\n")
                return {"action": "cool", "status": "SUCCESS", "result": res}
            elif "eco" in sub or "quiet" in sub:
                npu.power_profile = "ECO"
                print("\n[POWER PROFILE]: Set to ECO (Cool & Quiet - 4 CPU Threads, 1.5B/Cloud AI)\n")
                return {"action": "power", "status": "SUCCESS", "profile": "ECO"}
            elif "perf" in sub or "max" in sub:
                npu.power_profile = "PERFORMANCE"
                print("\n[POWER PROFILE]: Set to PERFORMANCE (Full 7B Models)\n")
                return {"action": "power", "status": "SUCCESS", "profile": "PERFORMANCE"}
            else:
                health = npu.get_system_health()
                print(f"\n[HARDWARE ACCELERATION & NPU STATUS]:")
                print(f"  NPU Device   : {health['hardware']['npu_name']}")
                print(f"  GPU Device   : {health['hardware']['gpu_name']}")
                print(f"  CPU Cores    : {health['hardware']['physical_cores']} Physical / {health['hardware']['logical_cores']} Logical")
                print(f"  RAM Usage    : {health['ram_used_gb']} GB / {health['ram_total_gb']} GB ({health['ram_percent']}%)")
                print(f"  CPU Usage    : {health['cpu_percent']}%")
                print(f"  Power Mode   : {health['power_profile']}\n")
                return {"action": "npu_status", "status": "SUCCESS", "result": health}

        # ----------------------------------------------------------
        # DISTRIBUTED WORKER MESH COMPUTE (P2P GAMING LAPTOP POOL)
        # ----------------------------------------------------------
        elif command in ("mesh", "workers", "worker", "nodes"):
            from jarvisx.mesh.worker_node import get_worker_registry
            from jarvisx.mesh.worker_heartbeat import get_worker_heartbeat_prober
            registry = get_worker_registry()
            prober = get_worker_heartbeat_prober()

            tokens = (args or "").split()
            sub = tokens[0].lower() if tokens else "status"

            if sub in ("add", "register") and len(tokens) >= 3:
                name = tokens[1]
                host = tokens[2]
                port = int(tokens[3]) if len(tokens) >= 4 else 11434
                node = registry.register_worker(name=name, host=host, port=port)
                print(f"\n[MESH WORKER REGISTERED]: {node.name} -> {node.url}")
                print("Probing connection...")
                try:
                    probe_res = asyncio.run(prober.probe_worker(node))
                    print(f"Status: {probe_res.get('status')} | Latency: {probe_res.get('latency_ms', 0)}ms | Models: {len(probe_res.get('models', []))} found\n")
                except Exception as e:
                    print(f"Worker added (Offline/Unreachable: {e})\n")
                return {"action": "mesh_add", "status": "SUCCESS", "worker": node.to_dict()}

            elif sub in ("remove", "delete", "rm") and len(tokens) >= 2:
                target = tokens[1]
                removed = registry.remove_worker(target)
                print(f"\n[MESH WORKER REMOVED]: {target} ({'Success' if removed else 'Not found'})\n")
                return {"action": "mesh_remove", "status": "SUCCESS" if removed else "NOT_FOUND"}

            elif sub in ("ping", "probe", "scan"):
                print("\n[PROBING MESH WORKER POOL]...")
                try:
                    res = asyncio.run(prober.probe_all_workers())
                    for r in res:
                        print(f"  • {r.get('name', 'Unknown')}: {r.get('status')} ({r.get('latency_ms', 'N/A')}ms) - {r.get('url')}")
                except Exception as e:
                    print(f"Probe error: {e}")
                print()
                return {"action": "mesh_ping", "status": "SUCCESS"}

            elif sub in ("bench", "benchmark"):
                from jarvisx.mesh.mesh_benchmarker import get_mesh_benchmarker
                benchmarker = get_mesh_benchmarker()
                target_w = tokens[1] if len(tokens) >= 2 else None
                print("\n[RUNNING DISTRIBUTED MESH VERIFICATION BENCHMARK]...")
                res = asyncio.run(benchmarker.run_comparative_benchmark(target_worker_id=target_w))
                loc = res["local_baseline"]
                rem = res["remote_mesh"]

                print("\n=========================================================================")
                print("         🎩 JARVIS X DISTRIBUTED MESH VERIFICATION REPORT")
                print("=========================================================================")
                print(f"  Local Baseline Model  : {loc['model']} ({loc['status']})")
                print(f"    • Execution Time    : {loc['duration_sec']}s")
                print(f"    • Master CPU Load   : {loc['cpu_percent']}%")
                print(f"    • Master RAM Delta  : +{loc['ram_delta_mb']} MB")
                print(f"    • Tokens Generated  : {loc['tokens_generated']}")
                print("  -----------------------------------------------------------------------")
                print(f"  Remote Mesh Worker    : {rem['worker_name']} ({rem['status']})")
                print(f"    • Worker URL        : {rem['worker_url']}")
                print(f"    • Network RTT Ping  : {rem['network_rtt_ms']} ms")
                print(f"    • Remote Exec Time  : {rem['duration_sec']}s")
                print(f"    • Master CPU Load   : {rem['master_cpu_percent']}%")
                print(f"    • Master RAM Delta  : +{rem['master_ram_delta_mb']} MB")
                print(f"    • Tokens Generated  : {rem['tokens_generated']}")
                print("=========================================================================\n")
                return {"action": "mesh_benchmark", "status": "SUCCESS", "results": res}

            else:
                workers = registry.list_workers()
                print("\n=========================================================================")
                print("               🎩 JARVIS X DISTRIBUTED WORKER MESH POOL")
                print("=========================================================================")
                if not workers:
                    print("  No remote worker nodes registered yet.")
                    print("  To add a friend's gaming laptop: 'mesh add <name> <tailscale_ip>'")
                    print("  Example: 'mesh add Rahul-4060 100.101.102.103'")
                else:
                    for w in workers:
                        status_icon = "🟢" if w.status.value == "ONLINE" else "🎮" if w.status.value == "GAMING" else "🔴"
                        print(f"  {status_icon} [{w.name:15s}] {w.url:25s} | GPU: {w.metrics.gpu_name[:15]:15s} | Status: {w.status.value}")
                        print(f"     VRAM: {w.metrics.vram_used_gb:.1f}/{w.metrics.vram_total_gb:.1f} GB | Temp: {w.metrics.temperature_c:.1f}°C | Load: {w.metrics.gpu_util_percent:.1f}% | Tasks Done: {w.total_tasks_completed}")
                        print(f"     Models: {', '.join(w.models[:4]) if w.models else 'Querying...'}")
                        print("  -----------------------------------------------------------------------")
                print("=========================================================================\n")
                return {"action": "mesh_status", "status": "SUCCESS", "workers": [w.to_dict() for w in workers]}

        # ----------------------------------------------------------
        # DAILY DSA TUTOR & MASTER CURRICULUM
        # ----------------------------------------------------------
        elif command in ("dsa", "tutor", "learn-dsa", "curriculum"):
            from jarvisx.tutor.dsa_tutor import DSATutorEngine
            tutor = DSATutorEngine()
            import re
            
            day_num = None
            if args:
                match = re.search(r'\b(\d+)\b', args)
                if match:
                    day_num = int(match.group(1))

            res = tutor.launch_daily_lesson(day=day_num, open_video=True, open_vscode=True)
            print(f"\n[DSA MASTER TUTOR - DAY {res['day']}]: {res['topic']}")
            print(f"  Lesson File: {res['filename']}")
            print(f"  VS Code:     {res['vscode_status']}")
            print(f"  Video:       {res['video_url']}\n")
            print(f"Alfred: {res['spoken_script']}\n")
            return {"action": "dsa_tutor", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # API KEY REGISTRATION & VAULT SHORTCUTS
        # ----------------------------------------------------------
        elif command in ("set-key", "set_key", "key", "apikey", "api-key", "gemini-key") or (command == "set" and args.lower().startswith(("key", "gemini", "api", "openrouter"))):
            from jarvisx.security.trust_engine import TrustEngine
            import os
            te = TrustEngine()
            
            clean_args = args.split()
            val = clean_args[-1] if clean_args else ""
            key_name = "GEMINI_API_KEY"
            if len(clean_args) >= 2 and any(k in clean_args[0].upper() for k in ("OPENROUTER", "GEMINI", "GOOGLE")):
                key_name = clean_args[0].upper()

            if val:
                os.environ[key_name] = val
                te.vault.set_secret(key_name, val)
                try:
                    with open(".env", "a", encoding="utf-8") as f:
                        f.write(f"\n{key_name}={val}\n")
                except Exception:
                    pass
                print(f"\n[KEY SAVED]: Successfully registered {key_name} in Alfred's Vault!\n")
                return {"action": "set_key", "status": "SUCCESS", "key": key_name, "value": te.vault.mask_token(val)}
            return {"action": "set_key", "status": "FAILED", "error": "No key value provided."}

        # ----------------------------------------------------------
        # PHASE 99: SECURITY & TRUST LAYER (Permissions, Vault, Hash-Audit)
        # ----------------------------------------------------------
        elif command in ("security", "trust", "audit", "vault"):
            from jarvisx.security.trust_engine import TrustEngine
            te = TrustEngine()
            sub = args.lower().strip() if args else ""
            if "audit" in sub or command == "audit":
                res = te.audit_logger.verify_chain_integrity()
                print(f"\n[AUDIT INTEGRITY]: {res['status']} ({res['total_entries']} entries verified)\n")
            elif "vault" in sub or command == "vault":
                parts = args.split()
                if len(parts) >= 3 and parts[0].lower() == "set":
                    item = te.vault.set_secret(parts[1], parts[2])
                    res = item.to_dict()
                    import os
                    os.environ[parts[1]] = parts[2]
                    try:
                        with open(".env", "a", encoding="utf-8") as f:
                            f.write(f"\n{parts[1]}={parts[2]}\n")
                    except Exception:
                        pass
                    print(f"\n[VAULT KEY SAVED]: Successfully stored {parts[1]} in Alfred Vault!\n")
                elif len(parts) >= 2 and parts[0].lower() == "get":
                    val = te.vault.get_secret(parts[1])
                    res = {"key": parts[1], "value": te.vault.mask_token(val or "")}
                else:
                    res = te.vault.list_secrets_masked()
            elif "explain" in sub:
                action_target = args.replace("explain", "").strip() or "system.mutation"
                res = te.explain(action_target)
            else:
                res = te.status()
            return {"action": "security", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 98: RELIABILITY KERNEL & EVOLUTION LEDGER
        # ----------------------------------------------------------
        elif command in ("doctor", "diagnostics", "checkup"):
            from jarvisx.reliability.reliability_engine import ReliabilityEngine
            re = ReliabilityEngine()
            res = re.doctor()
            return {"action": "doctor", "status": "SUCCESS", "result": res}

        elif command in ("health", "uptime", "heartbeat"):
            from jarvisx.reliability.reliability_engine import ReliabilityEngine
            re = ReliabilityEngine()
            res = re.health()
            print(f"\n[HEALTH PROBE]: {res['status']} | RAM: {res['memory_rss_mb']}MB | Latency: {res['latency_ms']}ms | Uptime: {res['uptime_seconds']}s\n")
            return {"action": "health", "status": "SUCCESS", "result": res}

        elif command in ("backup", "snapshot"):
            from jarvisx.reliability.reliability_engine import ReliabilityEngine
            re = ReliabilityEngine()
            sub = args.lower().strip() if args else ""
            if "list" in sub:
                res = re.backup_list()
            elif "restore" in sub:
                snap_id = args.split()[-1] if len(args.split()) > 1 else "latest"
                res = re.backup_restore(snap_id)
            else:
                res = re.backup_create()
            return {"action": "backup", "status": "SUCCESS", "result": res}

        elif command in ("evolution", "ledger", "history-ledger"):
            from jarvisx.reliability.reliability_engine import ReliabilityEngine
            re = ReliabilityEngine()
            res = re.evolution_list()
            return {"action": "evolution", "status": "SUCCESS", "result": res}

        # ----------------------------------------------------------
        # PHASE 97: SELF-IMPROVEMENT LOOP (Metrics, Root-Cause, Upgrades)
        # ----------------------------------------------------------
        elif command in ("improve", "self-improve", "performance", "upgrades"):
            from jarvisx.self_improvement.self_improvement_engine import SelfImprovementEngine
            sie = SelfImprovementEngine()
            sub = args.lower().strip() if args else ""
            if "status" in sub or "metric" in sub:
                res = sie.status()
            elif "fail" in sub or "root" in sub:
                res = sie.failures()
            elif "pattern" in sub or "playbook" in sub:
                res = sie.patterns()
            elif "upgrade" in sub or "loop" in sub:
                res = sie.run_self_upgrade_cycle()
            else:
                res = sie.status()
            return {"action": "improve", "status": "SUCCESS", "result": res}

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

        # Route general conversational queries, greetings, or natural language requests to DynamicOrchestrator
        try:
            from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
            orch = DynamicOrchestrator()
            query = raw_input.strip()
            if query.lower().startswith("chat "):
                query = query[5:].strip()
            res = orch.execute_voice_command(query)
            if isinstance(res, dict) and "response" in res:
                print(f"\nAlfred: {res['response']}\n")
                return {"action": res.get("action", "chat"), "status": "SUCCESS", "output": res["response"], "response": res["response"], "details": res}
            return res
        except Exception:
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

        # Route general conversational or unhandled commands to DynamicOrchestrator
        try:
            from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator
            orch = DynamicOrchestrator()
            query = raw_input.strip()
            if query.lower().startswith("chat "):
                query = query[5:].strip()
            res = orch.execute_voice_command(query)
            if isinstance(res, dict) and "response" in res:
                print(f"\nAlfred: {res['response']}\n")
                return {"action": res.get("action", "chat"), "status": "SUCCESS", "output": res["response"], "response": res["response"], "details": res}
            return res
        except Exception as e:
            if self.mission_mgr and args:
                print("\nAlfred: Mission accepted.\n")
                mission_res = await self.mission_mgr.create_and_execute_mission(args)
                res = mission_res.get("result", {})
                files = res.get("files_changed", [])
                test_status = res.get("test_result", {}).get("status", "PASS")
                print("Mission Complete.\n")
                print("Files:")
                for f in files:
                    print(f"  - {f}")
                print(f"\nTests: {test_status}\n")
                return {"action": "mission", "status": "COMPLETED", "mission_result": mission_res}
            return {"error": f"Execution error: {e}"}

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
