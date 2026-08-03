#!/usr/bin/env python3
"""
Jarvis X Main Production Entry Point
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
from jarvisx.interface.cli import JarvisCLI


async def async_main():
    runtime = JarvisRuntime()
    await runtime.start(print_banner=True)

    if len(sys.argv) > 1:
        raw_cmd = " ".join(sys.argv[1:])
        res = await runtime.cli.handle_command_async(raw_cmd)
        if raw_cmd.startswith("status") or raw_cmd.startswith("history"):
            print(json.dumps(res, indent=2))

def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
