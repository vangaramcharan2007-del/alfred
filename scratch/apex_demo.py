import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jarvisx.core.distraction_vault import GuardianMonitor
from jarvisx.core.ingestion.campusweb import CampusWebEngine
from jarvisx.tools.termux import TermuxTool

try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    RICH = True
except ImportError:
    RICH = False

def print_friday(msg):
    if RICH:
        console.print(f"\n[bold cyan]Friday[/bold cyan]: {msg}")
    else:
        print(f"\nFriday: {msg}")

def run_demo():
    if RICH:
        console.clear()
        console.print(Panel.fit(
            "[bold cyan]F R I D A Y[/bold cyan]",
            subtitle="[dim]Jarvis X  //  Protocol Omega Demo[/dim]",
            border_style="cyan",
        ))
        steps = [
            "OmniRoute LLM Gateway",
            "Termux Android Bridge",
            "Distraction Vault",
            "Waveform UI",
        ]
        for s in steps:
            time.sleep(0.3)
            console.print(f"  [green]+[/green] [dim]{s}[/dim]")
        console.print()
    else:
        print("\n  F R I D A Y")
        print("  Jarvis X  //  Protocol Omega Demo\n")
        
    time.sleep(1)
    print_friday("Systems online. Good morning. Let's get that 10 CGPA today.")
    time.sleep(2)
    
    # CampusWeb
    if RICH:
        console.print("\n[dim]-- Phase 1: Omni-Ingestion Pipeline --[/dim]")
        console.print("  [cyan]*[/cyan] Fetching live data from campusweb.in...")
    else:
        print("\n-- Phase 1: Omni-Ingestion Pipeline --")
        
    time.sleep(1)
    data = {"AOOP": "85%", "Maths": "92%", "OS": "78%"}
    if RICH:
        for k, v in data.items():
            console.print(f"    [dim]{k}: {v}[/dim]")
    print_friday(f"I've checked CampusWeb. Your AOOP attendance is {data.get('AOOP')}. Let's keep that up.")
    time.sleep(3)
    
    # Distraction Vault
    if RICH:
        console.print("\n[dim]-- Phase 2: The Distraction Vault --[/dim]")
        console.print("  [cyan]*[/cyan] Starting LeetCode focus block...")
    else:
        print("\n-- Phase 2: The Distraction Vault --")
        
    time.sleep(1)
    
    def on_distract(k):
        print_friday(f"Focus mode active. I intercepted '{k}'. Stay on task. We have a workout scheduled later.")
        
    guardian = GuardianMonitor(on_distract)
    guardian.engage_focus_mode()
    
    if RICH:
        console.print("  [red]![/red] [dim]User attempts to open 'YouTube - Google Chrome'[/dim]")
        console.print("  [red]X[/red] [bold red]INTERCEPT[/bold red] Process 'chrome.exe' forcefully terminated.")
    time.sleep(1)
    on_distract("youtube")
    time.sleep(2)
    
    # Termux
    if RICH:
        console.print("\n[dim]-- Phase 3: Android Handoff --[/dim]")
        console.print("  [green]+[/green] VIBRATE pulse sent via Termux API.")
        console.print("  [green]+[/green] NOTIFICATION pushed to Android Lock Screen.")
    time.sleep(3)
    
    # Web OS
    if RICH:
        console.print("\n[dim]-- Phase 4: Waveform UI --[/dim]")
        console.print("  [cyan]Waveform UI[/cyan] -> [link=http://127.0.0.1:8000]http://127.0.0.1:8000[/link]\n")
    
    time.sleep(2)
    if RICH:
        console.print("[bold cyan]Demo complete.[/bold cyan]\n")

if __name__ == "__main__":
    # Mock Termux
    import jarvisx.tools.termux
    class MockResult:
        def __init__(self):
            self.stdout = "Mock output"
            self.returncode = 0
    jarvisx.tools.termux.subprocess.run = lambda *args, **kwargs: MockResult()
    run_demo()
