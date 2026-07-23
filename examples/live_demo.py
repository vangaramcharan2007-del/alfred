import asyncio
import os
import sys
from pathlib import Path

src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from jarvisx.runtime import create_default_runtime


async def main():
    # Force Desktop context to ensure no Android mock responses are given
    os.environ["JARVIS_DEBUG"] = "true"
    
    print("==================================================")
    print("          JARVIS X LIVE DEMO VALIDATION           ")
    print("==================================================\n")
    
    runtime = create_default_runtime()
    
    scenarios = [
        "hello Alfred",
        "open vscode",
        "open youtube",
        "research operating systems",
        "remember I have DSA tomorrow",
        "show my missions",
        "bye"
    ]

    for cmd in scenarios:
        print(f"\nJarvis> {cmd}")
        response = await runtime.alfred.process(cmd, trace_id="trace-demo")
        print(f"Alfred: {response.message}")
        
    print("\n==================================================")
    print("                 DEMO COMPLETE                    ")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(main())
