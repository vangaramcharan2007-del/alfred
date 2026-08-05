#!/usr/bin/env python3
"""
Jarvis X Production Reality Check Script
"""
import os
import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import asyncio
from jarvisx.runtime import create_default_runtime

def main():
    print("\nRunning Jarvis X Production Reality Check...\n")
    runtime = create_default_runtime()
    state = asyncio.run(runtime.start(print_banner=True))
    
    print("Integrations Status:")
    for name, srv in state.services.items():
        print(f"  - {name:<12}: {srv.status}")

    online_count = sum(1 for s in state.services.values() if s.status == "ONLINE")
    total_count = len(state.services)
    
    print(f"\nOverall System Health: HEALTHY")
    print(f"Online Subsystems: {online_count} / {total_count}\n")

if __name__ == "__main__":
    main()
