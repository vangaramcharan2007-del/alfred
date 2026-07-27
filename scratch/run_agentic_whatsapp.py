import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath("src"))
from jarvisx.runtime import create_default_runtime

async def main():
    print("======================================================")
    print("  JARVIS X: NATIVE MULTI-AGENT WHATSAPP & EXCEL DEMO  ")
    print("======================================================")
    
    runtime = create_default_runtime()
    
    try:
        with open("scratch/whatsapp_data.txt", "r", encoding="utf-8") as f:
            raw_data = f.read()
    except Exception:
        raw_data = "No data found."
        
    prompt = f"you know the drill alfred do the excel and send the 4 files to ravindar vanga in whatasaap infront of my eyes with voice\n\n{raw_data}"
    
    print("\n[User Prompt]:", prompt.split('\n')[0], "...\n")
    print("[*] Routing request via Alfred Orchestrator...\n")
    
    from jarvisx.agents.alfred import _speak_offline
    _speak_offline("Alfred here. Processing your WhatsApp request.", voice_hint="male")
    
    response = await runtime.alfred.process(prompt, trace_id="whatsapp-demo")
    
    print(f"\n[Agent Response - {response.agent_id.upper()}]:\n{response.message}")
    print("\n[*] Demonstration Completed. Keeping script alive for voice rendering to finish...")
    await asyncio.sleep(10)
    
if __name__ == "__main__":
    asyncio.run(main())
