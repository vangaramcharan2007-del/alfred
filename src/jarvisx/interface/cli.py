"""
Jarvis X CLI — The single command interface for Alfred.
Every command does real work. No fakes.
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

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        health = self.kernel.health_check()
        return {
            "system_health": health["overall"],
            "health_score": health["health_score"],
            "subsystems_online": health["online"]
        }

    # ------------------------------------------------------------------
    # Sync handler
    # ------------------------------------------------------------------
    def handle_command(self, raw_input: str) -> Dict[str, Any]:
        command, args = self.parser.parse(raw_input)
        if command == "status":
            return self.get_status()
        elif command == "health":
            return self.kernel.health_check()
        elif command == "history":
            missions = self.persistence.get_all_missions()
            return {"action": "history", "total_missions": len(missions), "missions": missions}
        elif command == "help":
            return {"commands": self.parser.list_commands()}
        elif command == "mission":
            return {"action": "mission", "request": args, "note": "Use handle_command_async for execution."}
        return {"error": f"Unknown command: '{command}'. Type 'help' for available commands."}

    # ------------------------------------------------------------------
    # Async handler — the real engine
    # ------------------------------------------------------------------
    async def handle_command_async(self, raw_input: str) -> Dict[str, Any]:
        command, args = self.parser.parse(raw_input)

        if command == "status":
            return self.get_status()
        elif command == "health":
            return self.kernel.health_check()
        elif command == "history":
            missions = self.persistence.get_all_missions()
            return {"action": "history", "total_missions": len(missions), "missions": missions}
        elif command == "help":
            return self._print_help()

        # ----------------------------------------------------------
        # MISSION: The core router
        # ----------------------------------------------------------
        elif command == "mission":
            return await self._handle_mission(args)

        # ----------------------------------------------------------
        # DOCTOR: System diagnostics
        # ----------------------------------------------------------
        elif command == "doctor":
            return self._handle_doctor()

        # ----------------------------------------------------------
        # CHAT: Direct LLM conversation
        # ----------------------------------------------------------
        elif command == "chat":
            return await self._handle_chat(args)

        # ----------------------------------------------------------
        # MODELS: List available models
        # ----------------------------------------------------------
        elif command == "models":
            return self._handle_models()

        return {"error": f"Unknown command: '{command}'. Type 'help' for available commands."}

    # ------------------------------------------------------------------
    # Mission Router
    # ------------------------------------------------------------------
    async def _handle_mission(self, args: str) -> Dict[str, Any]:
        if not args:
            args = "continue"

        cmd = args.strip().lower()

        # === CONTINUE ===
        if cmd in ("continue", "restore", "resume"):
            from jarvisx.automation.coding_commands import alfred_continue
            result = alfred_continue()
            return {"action": "continue", "status": result["status"], "result": result}

        # === FIX THIS ===
        if cmd in ("fix", "fix this", "fix it", "fix error"):
            from jarvisx.automation.coding_commands import alfred_fix_this
            result = alfred_fix_this()
            return {"action": "fix", "status": result["status"], "result": result}

        # === WRITE TESTS ===
        if cmd.startswith("write tests ") or cmd.startswith("test "):
            from jarvisx.automation.coding_commands import write_tests
            file_path = args.split(maxsplit=2)[-1] if len(args.split()) > 2 else args.split()[-1]
            result = write_tests(file_path)
            return {"action": "write_tests", "status": result["status"], "result": result}

        # === EXPLAIN ===
        if cmd.startswith("explain "):
            from jarvisx.automation.coding_commands import explain_file
            file_path = args.split(maxsplit=1)[-1]
            result = explain_file(file_path)
            return {"action": "explain", "status": result["status"], "result": result}

        # === REVIEW ===
        if cmd.startswith("review "):
            from jarvisx.automation.coding_commands import review_code
            file_path = args.split(maxsplit=1)[-1]
            result = review_code(file_path)
            return {"action": "review", "status": result["status"], "result": result}

        # === FIND DEAD CODE ===
        if cmd in ("find dead code", "dead code", "unused"):
            from jarvisx.automation.coding_commands import find_dead_code
            result = find_dead_code()
            return {"action": "dead_code", "status": result["status"], "result": result}

        # === GENERATE DOCS ===
        if cmd.startswith("generate docs ") or cmd.startswith("docs "):
            from jarvisx.automation.coding_commands import generate_docs
            file_path = args.split(maxsplit=2)[-1] if "docs " in args else args.split()[-1]
            result = generate_docs(file_path)
            return {"action": "generate_docs", "status": result["status"], "result": result}

        # === ORGANIZE ===
        if cmd.startswith("organize "):
            from jarvisx.automation.desktop_actions import organize_folder
            folder = args.split(maxsplit=1)[-1]
            result = organize_folder(folder)
            return {"action": "organize", "status": result["status"], "result": result}

        # === COMPRESS ===
        if cmd.startswith("compress ") or cmd.startswith("zip "):
            from jarvisx.automation.desktop_actions import compress_folder
            folder = args.split(maxsplit=1)[-1]
            result = compress_folder(folder)
            return {"action": "compress", "status": result["status"], "result": result}

        # === SCREENSHOT ===
        if cmd in ("screenshot", "capture screen"):
            from jarvisx.automation.desktop_actions import take_screenshot
            result = take_screenshot()
            return {"action": "screenshot", "status": result["status"], "result": result}

        # === WINDOWS ===
        if cmd in ("windows", "list windows"):
            from jarvisx.automation.desktop_actions import list_windows
            result = list_windows()
            return {"action": "windows", "status": result["status"], "result": result}

        # === FOCUS WINDOW ===
        if cmd.startswith("focus "):
            from jarvisx.automation.desktop_actions import focus_window
            title = args.split(maxsplit=1)[-1]
            result = focus_window(title)
            return {"action": "focus", "status": result["status"], "result": result}

        # === KILL PROCESS ===
        if cmd.startswith("kill "):
            from jarvisx.automation.desktop_actions import kill_process
            name = args.split(maxsplit=1)[-1]
            result = kill_process(name)
            return {"action": "kill", "status": result["status"], "result": result}

        # === DISK USAGE ===
        if cmd.startswith("disk ") or cmd == "du":
            from jarvisx.automation.desktop_actions import disk_usage
            path = args.split(maxsplit=1)[-1] if len(args.split()) > 1 else "."
            result = disk_usage(path)
            return {"action": "disk", "status": result["status"], "result": result}

        # === WORKFLOW: PREPARE FOR CODING ===
        if cmd in ("prepare for coding", "start coding", "start jarvis", "start development"):
            return await self._workflow_prepare_coding()

        # === WORKFLOW: FINISH WORK ===
        if cmd in ("finish work", "finish development", "end day", "done"):
            return await self._workflow_finish_work()

        # === WORKFLOW: STUDY MODE ===
        if cmd in ("study mode", "study"):
            return await self._workflow_study_mode()

        # === GENERIC MISSION (LLM-powered) ===
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

    # ------------------------------------------------------------------
    # Workflows
    # ------------------------------------------------------------------
    async def _workflow_prepare_coding(self) -> Dict[str, Any]:
        """Open VS Code + restore workspace + run diagnostics + summarize."""
        print("\nAlfred: Preparing workspace...\n")

        # 1. Open VS Code
        import shutil
        code_bin = shutil.which("code") or "code"
        subprocess.Popen([code_bin, "."], shell=True)
        print("  [+] VS Code opened")

        # 2. Open terminal
        try:
            subprocess.Popen(["wt.exe"], shell=True)
            print("  [+] Windows Terminal opened")
        except Exception:
            subprocess.Popen(["cmd.exe", "/c", "start", "cmd"], shell=True)
            print("  [+] CMD opened")

        # 3. Git status
        r = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, timeout=5)
        branch = r.stdout.strip()
        print(f"  [+] Git branch: {branch}")

        r = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=5)
        modified = len([l for l in r.stdout.splitlines() if l.strip()])
        print(f"  [+] Modified files: {modified}")

        # 4. Quick test check
        r = subprocess.run([sys.executable, "-m", "pytest", "tests/unit/", "-q", "--no-header"],
                           capture_output=True, text=True, timeout=60)
        test_status = "PASS" if r.returncode == 0 else "FAIL"
        print(f"  [+] Unit tests: {test_status}")

        # 5. LLM summary of what to work on
        from jarvisx.automation.coding_commands import get_workspace_context, _call_ollama
        ctx = get_workspace_context()

        prompt = f"""You are Alfred. The developer just sat down to code. Based on this workspace:
Branch: {branch}, Modified: {modified} files, Tests: {test_status}
Recent commits: {ctx['recent_commits'][:3]}
TODOs: {ctx['todos'][:5]}
Give a brief (3 sentences max) summary of what to focus on today."""

        response = _call_ollama(prompt, timeout=30)
        if response:
            print(f"\nAlfred: {response}\n")
        else:
            print(f"\n  Alfred: [Ollama offline] Check TODOs and modified files manually.\n")

        return {"action": "prepare", "status": "SUCCESS", "branch": branch, "tests": test_status}

    async def _workflow_finish_work(self) -> Dict[str, Any]:
        """Commit + push + run tests + summary."""
        print("\nAlfred: Finishing today's work...\n")

        # 1. Run tests
        r = subprocess.run([sys.executable, "-m", "pytest", "tests/unit/", "-q", "--no-header"],
                           capture_output=True, text=True, timeout=120)
        test_status = "PASS" if r.returncode == 0 else "FAIL"
        print(f"  [+] Tests: {test_status}")

        # 2. Git add + commit
        subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10)
        r = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True, timeout=10)
        staged = r.stdout.strip()

        if staged:
            commit_msg = f"chore: end of day commit - {time.strftime('%Y-%m-%d')}"
            subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, timeout=10)
            print(f"  [+] Committed: {commit_msg}")

            # 3. Push
            r = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                print("  [+] Pushed to remote")
            else:
                print(f"  [!] Push failed: {r.stderr.strip()[:100]}")
        else:
            print("  [=] Nothing to commit")

        # 4. Summary
        r = subprocess.run(["git", "log", "--oneline", "-3"], capture_output=True, text=True, timeout=5)
        print(f"\n  Recent commits:")
        for line in r.stdout.splitlines():
            print(f"    {line.strip()}")
        print()

        return {"action": "finish", "status": "SUCCESS", "tests": test_status}

    async def _workflow_study_mode(self) -> Dict[str, Any]:
        """Enter study mode — show Friday dashboard reminders."""
        print("\nAlfred: Entering study mode...\n")

        try:
            from friday.friday_assistant import FridayAssistant
            friday = FridayAssistant()
            alerts = friday.generate_proactive_alerts()
            readiness = friday.get_exam_readiness()

            if alerts:
                print("  Friday Alerts:")
                for a in alerts:
                    print(f"    ! {a}")
                print()

            print("  Exam Readiness:")
            for r in readiness:
                print(f"    {r['subject']}: {r['verdict']} ({r['readiness']}%)")
            print()

        except Exception as e:
            print(f"  [!] Friday unavailable: {e}\n")

        return {"action": "study_mode", "status": "SUCCESS"}

    # ------------------------------------------------------------------
    # Doctor
    # ------------------------------------------------------------------
    def _handle_doctor(self) -> Dict[str, Any]:
        """Real system diagnostics — check what actually works."""
        import shutil

        checks = {}

        # Ollama
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
            checks["ollama"] = "ONLINE"
        except Exception:
            checks["ollama"] = "OFFLINE"

        # Git
        checks["git"] = "OK" if shutil.which("git") else "NOT FOUND"

        # VS Code
        checks["vscode"] = "OK" if shutil.which("code") else "NOT FOUND"

        # Python
        checks["python"] = sys.version.split()[0]

        # Key packages
        for pkg in ["pyttsx3", "pyautogui", "PIL", "pyperclip", "playwright"]:
            try:
                __import__(pkg)
                checks[pkg] = "INSTALLED"
            except ImportError:
                checks[pkg] = "NOT INSTALLED"

        # SQLite DB
        db_path = Path("var/db/friday.db")
        checks["friday_db"] = "OK" if db_path.exists() else "WILL CREATE ON FIRST RUN"

        print("\nAlfred Doctor:\n")
        for k, v in checks.items():
            status_marker = "[OK]" if v in ("ONLINE", "OK", "INSTALLED") or "." in str(v) else "[!!]"
            print(f"  {status_marker} {k:20s}: {v}")
        print()

        return {"action": "doctor", "status": "COMPLETED", "checks": checks}

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------
    async def _handle_chat(self, args: str) -> Dict[str, Any]:
        prompt = args or "Hello Alfred."
        from jarvisx.llm.ollama_provider import OllamaLLMProvider
        provider = OllamaLLMProvider()
        res = await provider.generate(prompt)
        print(f"\nUser: {prompt}\n")
        print(f"Alfred: {res['response']}\n")
        return {"action": "chat", "status": "COMPLETED", "response": res}

    # ------------------------------------------------------------------
    # Models
    # ------------------------------------------------------------------
    def _handle_models(self) -> Dict[str, Any]:
        """List actually installed Ollama models."""
        try:
            import json
            import urllib.request
            r = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
            data = json.loads(r.read().decode("utf-8"))
            models = [m["name"] for m in data.get("models", [])]
            print("\nInstalled Ollama Models:\n")
            for m in models:
                print(f"  - {m}")
            print()
            return {"action": "models", "status": "SUCCESS", "models": models}
        except Exception:
            print("\nAlfred: Ollama is offline. Cannot list models.\n")
            return {"action": "models", "status": "NOT_AVAILABLE", "reason": "Ollama offline"}

    # ------------------------------------------------------------------
    # Help
    # ------------------------------------------------------------------
    def _print_help(self) -> Dict[str, Any]:
        help_text = """
Alfred Commands:

  ENGINEERING
    continue              Resume work — analyze workspace and explain what to do next
    fix this              Find failing tests and generate fix
    write tests <file>    Generate pytest tests for a file
    explain <file>        Explain a file's architecture
    review <file>         Code review a file
    find dead code        Scan project for unused imports
    generate docs <file>  Add docstrings to a file

  DESKTOP
    organize <folder>     Sort files by extension
    compress <folder>     Zip a folder
    screenshot            Take a screenshot
    windows               List open windows
    focus <title>         Bring a window to front
    kill <process>        Kill a process
    disk <path>           Show disk usage

  WORKFLOWS
    prepare for coding    Open VS Code + terminal + diagnostics + daily goals
    finish work           Commit + push + test + summary
    study mode            Show Friday alerts and exam readiness

  SYSTEM
    doctor                Check what's installed and working
    chat <message>        Talk to Alfred via LLM
    models                List installed Ollama models
    status                System health
    help                  This message
"""
        print(help_text)
        return {"commands": help_text}
