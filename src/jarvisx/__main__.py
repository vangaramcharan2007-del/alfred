from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from jarvisx.api import create_alfred_api_server
from jarvisx.runtime import create_default_runtime


async def _run(message: str) -> int:
    runtime = create_default_runtime(log_path=Path("var/log/jarvisx.jsonl"))
    response = await runtime.alfred.process(message)
    print(json.dumps(response.to_dict(), indent=2, sort_keys=True))
    return 0 if response.handled else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Project Jarvis X task.")
    parser.add_argument("message", nargs="*", help="User task to route through Alfred.")
    parser.add_argument("--serve", action="store_true", help="Start Alfred's local REST API.")
    parser.add_argument("--host", default="127.0.0.1", help="REST API host.")
    parser.add_argument("--overlay", action="store_true", help="Launch the persistent desktop UI overlay and background voice engine.")
    args = parser.parse_args()
    
    if args.overlay:
        import subprocess
        import sys
        
        # Launch UI as a separate process so it has its own main thread
        print("Starting Jarvis X Desktop Overlay...")
        subprocess.Popen([sys.executable, "-m", "jarvisx.ui.overlay"])
        
        # Start the background voice engine
        runtime = create_default_runtime(log_path=Path("var/log/jarvisx.jsonl"))
        from jarvisx.core.continuous_voice import ContinuousVoiceEngine
        voice_engine = ContinuousVoiceEngine(runtime)
        voice_engine.start()
        
        print("Jarvis X background services online. Say 'Friday' or 'Alfred' to activate.")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            voice_engine.stop()
            return 0
            
    elif args.serve:
        runtime = create_default_runtime(log_path=Path("var/log/jarvisx.jsonl"))
        server = create_alfred_api_server(runtime, host=args.host, port=args.port)
        host, port = server.server_address
        print(f"Alfred REST API listening on http://{host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            return 0
        finally:
            server.server_close()
    if not args.message:
        parser.error("message is required unless --serve is used")
    return asyncio.run(_run(" ".join(args.message)))


if __name__ == "__main__":
    raise SystemExit(main())
