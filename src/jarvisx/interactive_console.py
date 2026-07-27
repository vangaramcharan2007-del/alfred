import os
import sys
import asyncio
import threading
import time

if hasattr(os, 'add_dll_directory'):
    dll_path = os.path.join(os.path.dirname(__file__), "..", "..", "ffmpeg-shared", "ffmpeg-master-latest-win64-gpl-shared", "bin")
    if os.path.exists(dll_path):
        os.add_dll_directory(dll_path)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from jarvisx.runtime import create_default_runtime
from jarvisx.core.state import update_agent_state

try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    RICH = True
except ImportError:
    RICH = False
    console = None


def boot():
    """Minimal cinematic boot — no bloat."""
    if RICH:
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]F R I D A Y[/bold cyan]",
            subtitle="[dim]Jarvis X  //  Protocol Omega[/dim]",
            border_style="cyan",
        ))
        steps = [
            "OmniRoute LLM Gateway",
            "Termux Android Bridge",
            "Distraction Vault",
            "Waveform UI",
        ]
        for s in steps:
            time.sleep(0.15)
            console.print(f"  [green]+[/green] [dim]{s}[/dim]")
        console.print()
    else:
        print("\n  F R I D A Y")
        print("  Jarvis X  //  Protocol Omega\n")


def start_web_os():
    """Launch the waveform dashboard in background."""
    try:
        from jarvisx.api.server import run_server
        threading.Thread(target=run_server, daemon=True, name="WebOS").start()
        if RICH:
            console.print("  [cyan]Waveform UI[/cyan] -> [link=http://127.0.0.1:8000]http://127.0.0.1:8000[/link]\n")
        else:
            print("  Waveform UI -> http://127.0.0.1:8000\n")
    except Exception:
        pass


async def main():
    boot()
    start_web_os()

    # Ensure config
    os.makedirs("config", exist_ok=True)

    # Init Friday state
    update_agent_state("friday", "friday_introduced", True)
    update_agent_state("friday", "friday_greeted", False)
    update_agent_state("friday", "mission_stage", "idle")
    update_agent_state("friday", "correction_attempts", 0)

    runtime = create_default_runtime()

    if RICH:
        console.print("[bold cyan]Systems online.[/bold cyan] Talk to Friday.\n")
    else:
        print("Systems online. Talk to Friday.\n")

    while True:
        try:
            user_input = input("You: ")
            if user_input.strip().lower() in ("exit", "quit", "bye"):
                if RICH:
                    console.print("\n[dim]Shutting down. See you tomorrow, sir.[/dim]")
                else:
                    print("\nShutting down. See you tomorrow, sir.")
                break

            if not user_input.strip():
                continue

            # Route through Alfred -> Friday
            response = await runtime.alfred.process(user_input, trace_id="console")

            if RICH:
                console.print(f"\n[bold cyan]Friday[/bold cyan]: {response.message}\n")
            else:
                print(f"\nFriday: {response.message}\n")

        except KeyboardInterrupt:
            print("\nShutting down.")
            break
        except Exception as e:
            print(f"\n[Error]: {e}")


if __name__ == "__main__":
    asyncio.run(main())
