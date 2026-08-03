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
from pathlib import Path

# Ensure src directory is in sys.path
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import json
import asyncio
from jarvisx.runtime.runtime import JarvisRuntime


async def async_main():
    runtime = JarvisRuntime()
    await runtime.start(print_banner=True)

    if len(sys.argv) > 1:
        raw_cmd = " ".join(sys.argv[1:])

        top_commands = {
            "status", "health", "history", "help", "doctor", "chat", "models",
            "briefing", "context", "daily", "war", "academic", "cgpa",
            "daemon", "report", "time-saved", "metrics", "voice", "assistant"
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


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
