import os
import sys
import asyncio
import threading
import time

if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\Users\vanga\Documents\Codex\2026-07-11\files-mentioned-by-the-user-you\outputs\project-jarvis-x\ffmpeg-shared\ffmpeg-master-latest-win64-gpl-shared\bin")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from jarvisx.runtime import create_default_runtime
from jarvisx.core.state import update_agent_state

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.text import Text
    rich_available = True
except ImportError:
    rich_available = False

async def print_message(text: str):
    if rich_available:
        Console().print(f"\n[bold cyan]Friday[/bold cyan]: {text}\n")
    else:
        print(f"\n[Friday]: {text}\n")

async def main():
    if rich_available:
        console = Console()
        console.clear()
        
        # Cinematic Boot Sequence
        console.print(Panel.fit("[bold cyan]J A R V I S   X   //   P R O T O C O L   O M E G A[/bold cyan]", border_style="cyan"))
        
        with Progress(
            SpinnerColumn(spinner_name="line"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="cyan", finished_style="green"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            t1 = progress.add_task("[cyan]Establishing Termux Android Bridge...", total=100)
            t2 = progress.add_task("[cyan]Connecting to OmniRoute LLM Gateway...", total=100)
            t3 = progress.add_task("[cyan]Initializing Distraction Vault (win32gui)...", total=100)
            t4 = progress.add_task("[cyan]Booting Industrial Web OS...", total=100)
            
            for i in range(100):
                time.sleep(0.01)
                progress.update(t1, advance=1)
                if i > 20: progress.update(t2, advance=1.25)
                if i > 40: progress.update(t3, advance=1.66)
                if i > 60: progress.update(t4, advance=2.5)

        # Start Web OS Background Thread
        try:
            from jarvisx.api.server import run_server
            threading.Thread(target=run_server, daemon=True, name="WebOS").start()
            console.print("[bold green]Web OS Dashboard running at http://127.0.0.1:8000[/bold green]")
        except ImportError:
            pass

        console.print("\n[bold cyan]System Online. Open mic active. Type 'exit' to quit.[/bold cyan]\n")
    else:
        print("="*60)
        print(" Jarvis X - Protocol Omega (Interactive Console)")
        print("="*60)
        print("\nSystem Online. Type 'exit' to quit.\n")
    
    # Ensure demo config exists
    os.makedirs("config", exist_ok=True)
    if not os.path.exists(os.path.join("config", "demo.json")):
        import json
        with open(os.path.join("config", "demo.json"), "w") as f:
            json.dump({
                "demo_mode": True,
                "typing_speed": 0.005,
                "action_delay": 0.5,
                "verbose_narration": True
            }, f)

    # Pre-configure Friday state for this demonstration sequence
    update_agent_state("friday", "friday_introduced", True)
    update_agent_state("friday", "friday_greeted", False)
    update_agent_state("friday", "mission_stage", "idle")
    update_agent_state("friday", "correction_attempts", 0)
    
    runtime = create_default_runtime()
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.strip().lower() in ['exit', 'quit']:
                print("Shutting down Jarvis X.")
                break
                
            if not user_input.strip():
                continue
                
            # Process via Alfred Orchestrator
            response = await runtime.alfred.process(user_input, trace_id="interactive-console")
            
            # Format and print the response
            await print_message(response.message)
                
        except KeyboardInterrupt:
            print("\nShutting down Jarvis X.")
            break
        except Exception as e:
            print(f"\n[System Error]: {e}")

if __name__ == "__main__":
    asyncio.run(main())
