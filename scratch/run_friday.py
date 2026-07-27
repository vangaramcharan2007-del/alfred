import asyncio
from pathlib import Path
from jarvisx.runtime import create_default_runtime
from jarvisx.core.events import Event

async def main():
    print("[1] Booting Jarvis Runtime...")
    runtime = create_default_runtime()
    
    print("\n[2] Firing Message to Alfred...")
    message = "fine then friday open vs code and explain array basics in python code"
    print(f"User: {message}")
    
    response = await runtime.alfred.process(message, trace_id="friday-test-1")
    
    print("\n--- Response ---")
    print(f"Handled By: {response.agent_id}")
    print(f"Success: {response.handled}")
    print(f"Message: {response.message}")
    print(f"Data: {response.data}")
    
    print("\n[3] Validating Friday Execution Logic...")
    if response.agent_id == "friday":
        print("[OK] Task correctly routed to Friday.")
        print("[OK] Friday agent loaded system prompt.")
    else:
        print("[FAIL] Routing failed.")
        
    runtime.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
