from typing import List, Dict, Any, Optional
import os
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn
from jarvisx.core.capabilities.evaluation import ProviderEvaluation


class MissionDashboard:
    """Live terminal UI for observing Alfred's internal state."""

    def __init__(self):
        self.console = Console()
        self.state = {
            "status": "Listening...",
            "wake_word": False,
            "command": "",
            "mission": {
                "running": False,
                "progress": 0,
                "current_step": "",
                "next_step": "",
                "capability": "",
                "provider": "",
                "status": ""
            },
            "negotiation": {
                "capability": "",
                "evaluations": [],
                "winner": ""
            },
            "memory": [],
            "tts": ""
        }

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def render(self):
        """Renders the dashboard based on the current state."""
        self.clear()
        
        # Header
        header = Text("ALFRED - LIVE RUNTIME", style="bold cyan", justify="center")
        self.console.print(Panel(header, border_style="cyan"))
        
        # Status Block
        status_text = Text()
        if self.state["wake_word"]:
            status_text.append("* Wake Word Detected\n", style="bold green")
        else:
            status_text.append(f"{self.state['status']}\n", style="dim")
            
        if self.state["command"]:
            status_text.append("\nCommand:\n", style="bold cyan")
            status_text.append(f'"{self.state["command"]}"', style="yellow")
            
        self.console.print(status_text)
        self.console.print("---------------------------------------", style="dim")
        
        # Mission Block
        if self.state["mission"]["running"] or self.state["mission"]["current_step"]:
            self.console.print("[bold cyan]Mission[/bold cyan]")
            self.console.print("Running", style="green" if self.state["mission"]["running"] else "yellow")
            self.console.print()
            self.console.print(f"[bold]Progress[/bold]\n{self.state['mission']['progress']}%")
            self.console.print()
            self.console.print(f"[bold]Current Step[/bold]\n{self.state['mission']['current_step']}")
            self.console.print()
            self.console.print(f"[bold]Next Step[/bold]\n{self.state['mission']['next_step']}")
            self.console.print()
            self.console.print(f"[bold]Capability[/bold]\n{self.state['mission']['capability']}")
            self.console.print()
            self.console.print(f"[bold]Provider[/bold]\n{self.state['mission']['provider']}")
            self.console.print()
            self.console.print(f"[bold]Status[/bold]\n{self.state['mission']['status']}")
            self.console.print("---------------------------------------", style="dim")
            
        # Negotiation Block
        if self.state["negotiation"]["evaluations"]:
            self.console.print("[bold cyan]Negotiation[/bold cyan]\n")
            self.console.print(f"{self.state['negotiation']['capability']}\n", style="magenta")
            
            for ev in self.state["negotiation"]["evaluations"]:
                self.console.print(f"{ev.provider_name}", style="bold white")
                self.console.print(f"{int(ev.score)}")
                self.console.print()
                
            self.console.print("[bold]Winner[/bold]\n", style="green")
            self.console.print(f"{self.state['negotiation']['winner']}\n", style="bold green")
            self.console.print("---------------------------------------", style="dim")
            
        # Memory Block
        if self.state["memory"]:
            self.console.print("[bold cyan]Memory[/bold cyan]\n")
            for item in self.state["memory"]:
                self.console.print(f"* {item}", style="green")
            self.console.print("\n---------------------------------------", style="dim")
            
        # TTS Block
        if self.state["tts"]:
            self.console.print("[bold cyan]TTS[/bold cyan]\n")
            self.console.print(f'"{self.state["tts"]}"', style="italic white")
            
        self.console.print("=======================================", style="cyan")

    # State update methods
    def set_listening(self, is_listening: bool):
        self.state["status"] = "Listening..." if is_listening else "Processing..."
        self.render()

    def set_wake_word(self, detected: bool):
        self.state["wake_word"] = detected
        self.render()

    def set_command(self, text: str):
        self.state["command"] = text
        self.render()

    def update_mission(self, **kwargs):
        self.state["mission"].update(kwargs)
        self.render()

    def set_negotiation(self, capability: str, evaluations: List[ProviderEvaluation], winner: str):
        self.state["negotiation"]["capability"] = capability
        self.state["negotiation"]["evaluations"] = evaluations
        self.state["negotiation"]["winner"] = winner
        self.render()
        
    def clear_negotiation(self):
        self.state["negotiation"] = {"capability": "", "evaluations": [], "winner": ""}
        self.render()

    def add_memory(self, memory_text: str):
        self.state["memory"].append(memory_text)
        self.render()

    def set_tts(self, text: str):
        self.state["tts"] = text
        self.render()
