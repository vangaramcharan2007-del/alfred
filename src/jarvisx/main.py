#!/usr/bin/env python3
"""
Jarvis X Main Production Entry Point.
Usage:
  python -m jarvisx                     # Interactive
  python -m jarvisx briefing            # Daily engineering context briefing
  python -m jarvisx war                 # Friday Academic War Mode (10 CGPA)
  python -m jarvisx daemon --start      # Start background daemon
  python -m jarvisx report              # Generate TIME_SAVED_REPORT.md
  python -m jarvisx continue            # Resume work
  python -m jarvisx fix this            # Fix failing tests
  python -m jarvisx help                # Show all commands
"""
import sys
import io
from pathlib import Path

# Ensure standard streams exist when run via pythonw (windowless execution)
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Ensure src directory is in sys.path
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import json
import asyncio
from jarvisx.runtime.runtime import JarvisRuntime


def _handle_engineering_command(cmd: str, args_list: list[str]) -> int:
    from jarvisx.engineering import (
        AdaptiveEngineeringAgent,
        DebugLoopEngine,
        ProjectIntelligence,
    )

    target_repo = args_list[0] if args_list else "."
    
    if cmd == "analyze":
        intel = ProjectIntelligence(target_repo)
        print(intel.analyze().generate_report())
        return 0

    elif cmd == "explain":
        intel = ProjectIntelligence(target_repo)
        info = intel.analyze()
        lines = [
            f"ARCHITECTURE EXPLANATION FOR REPOSITORY: '{info.root_path}'",
            f"Primary Architecture Style: {info.architecture_style}",
            f"Core Languages: {', '.join(info.languages)}",
            f"Key Frameworks: {', '.join(info.frameworks)}",
            f"Package Management: {info.package_manager} | Build System: {info.build_system}",
            f"Test Framework: {info.test_framework}",
            f"Detected Entry Points: {', '.join(info.entry_points)}",
            f"\nDesign Rationale & Tradeoffs:\n  The project employs a {info.architecture_style} pattern to isolate domain responsibilities and ensure extensible component modularity. External dependencies are encapsulated cleanly within dedicated adapters.",
        ]
        print("\n".join(lines))
        return 0

    elif cmd == "improve":
        agent = AdaptiveEngineeringAgent(target_repo)
        report = agent.execute_mission("Analyze repository risk areas and apply highest impact structural improvements.")
        print(report.generate_report())
        return 0

    elif cmd == "debug":
        debug_engine = DebugLoopEngine(target_repo)
        res = debug_engine.debug_repository()
        print(res.generate_report())
        return 0

    elif cmd == "engineer":
        goal = " ".join(args_list) if args_list else "General architectural optimization and verification."
        agent = AdaptiveEngineeringAgent(".")
        report = agent.execute_mission(goal)
        print(report.generate_report())
        return 0

    return 1


async def async_main():
    if len(sys.argv) > 1:
        first_word = sys.argv[1].lower()
        if first_word in {"analyze", "explain", "debug", "engineer"}:
            sys.exit(_handle_engineering_command(first_word, sys.argv[2:]))
        elif first_word in {"desktop", "app", "widget", "waveform", "overlay"}:
            from jarvisx.automation.glowing_waveform_overlay import launch_sovereign_waveform
            launch_sovereign_waveform()
            sys.exit(0)

    runtime = JarvisRuntime()
    await runtime.start(print_banner=True)

    if len(sys.argv) > 1:
        raw_cmd = " ".join(sys.argv[1:])

        top_commands = {
            "status", "health", "history", "help", "--help", "-h", "doctor", "chat", "models",
            "briefing", "context", "daily", "welcome", "announce", "greeting", "friday", "hud", "wake", "wakeword", "tactical",
            "daemon", "report", "time-saved", "metrics", "voice", "assistant",
            "benchmark", "autonomy", "eval", "cert", "certify", "certification",
            "security", "trust", "audit", "vault", "backup", "snapshot", "evolution", "improve", "team",
            "knowledge", "obsidian", "rag",
            "evaluate", "evaluation", "feedback", "intelligence",
            "memory", "mem", "remember", "profile",
            "daemon", "jarvisd", "alfred", "ask", "q",
            "coach", "study", "syllabus", "loop", "operate", "cycle"
        }
        first_word = sys.argv[1].lower()

        if first_word in top_commands:
            res = await runtime.cli.handle_command_async(raw_cmd)
        elif first_word == "mission":
            mission_args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            res = await runtime.cli.handle_command_async(f"mission {mission_args}")
        else:
            res = await runtime.cli.handle_command_async(f"mission {raw_cmd}")

        if first_word in {"status", "history"}:
            print(json.dumps(res, indent=2))
    else:
        print("\nType your commands at the 'alfred >' prompt. Type 'exit' or 'quit' to exit.\n")
        while True:
            try:
                user_input = input("alfred > ").strip()
                if not user_input:
                    continue
                if user_input.lower() in {"exit", "quit"}:
                    print("Exiting Alfred interactive session. Goodbye, Boss.")
                    break
                res = await runtime.cli.handle_command_async(user_input)
                if isinstance(res, dict) and "output" in res:
                    print(res["output"])
                elif isinstance(res, str):
                    print(res)
                else:
                    print(json.dumps(res, indent=2, default=str))
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Alfred interactive session. Goodbye, Boss.")
                break


def main():
    if len(sys.argv) > 1:
        first_word = sys.argv[1].lower()
        if first_word in {"desktop", "app", "widget", "waveform", "overlay"}:
            from jarvisx.automation.glowing_waveform_overlay import launch_sovereign_waveform
            try:
                launch_sovereign_waveform()
            except KeyboardInterrupt:
                print("\n[Alfred Overlay]: Closed cleanly.")
            return 0
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

