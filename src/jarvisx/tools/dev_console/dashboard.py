"""Generates the Rich TUI layout for the Developer Console."""
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from rich.text import Text
from rich.align import Align
from rich.console import Group

from jarvisx.tools.dev_console.state import ConsoleState
from jarvisx.tools.dev_console.command_router import CommandRouter

def generate_layout(state: ConsoleState, command_router: CommandRouter) -> Layout:
    """Builds the main TUI layout."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left_column", ratio=2),
        Layout(name="right_column", ratio=1)
    )
    
    layout["left_column"].split_column(
        Layout(name="dashboard", ratio=2),
        Layout(name="metrics", ratio=1)
    )
    
    layout["metrics"].split_row(
        Layout(name="performance"),
        Layout(name="recovery"),
        Layout(name="resources")
    )

    layout["right_column"].split_column(
        Layout(name="timeline", ratio=2),
        Layout(name="debug_state", ratio=1)
    )
    
    # Header
    header = Panel(Align.center(Text("JARVIS X EXECUTION CONSOLE", style="bold cyan")), style="blue")
    layout["header"].update(header)
    
    # Footer (Command Prompt)
    cmd_buffer = command_router.get_current_buffer() if command_router else ""
    footer = Panel(f"> {cmd_buffer}_", title="Command Input", style="green")
    layout["footer"].update(footer)
    
    with state.lock:
        _populate_dashboard(layout["dashboard"], state)
        _populate_performance(layout["performance"], state)
        _populate_recovery(layout["recovery"], state)
        _populate_resources(layout["resources"], state)
        _populate_timeline(layout["timeline"], state)
        _populate_debug_state(layout["debug_state"], state)
        
    return layout

def _populate_dashboard(layout: Layout, state: ConsoleState):
    table = Table.grid(padding=1)
    table.add_column(style="bold yellow", justify="right")
    table.add_column()
    
    table.add_row("Objective:", state.objective_name)
    table.add_row("Objective ID:", state.objective_id)
    table.add_row("Status:", state.objective_status)
    table.add_row("Worker:", state.worker_status)
    table.add_row("Queue Size:", str(state.queue_size))
    table.add_row("Scheduler Q:", str(state.scheduler_queue))
    table.add_row("DB Status:", state.db_status)
    
    # Progress Bar
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="blue"),
        TaskProgressColumn(),
        TextColumn("{task.completed}/{task.total}")
    )
    
    task_id = progress.add_task("Progress", total=state.total_steps, completed=state.current_step)
    
    details = Table.grid(padding=1)
    details.add_column(style="bold cyan")
    details.add_column()
    details.add_row("Remaining Steps:", str(state.remaining_steps))
    details.add_row("Current Action:", state.current_action)
    details.add_row("Current Target:", state.current_target)
    details.add_row("Checkpoint:", str(state.checkpoint_index))
    
    group = Group(table, Panel(progress), details)
    layout.update(Panel(group, title="Live Dashboard", border_style="bright_blue"))

def _populate_performance(layout: Layout, state: ConsoleState):
    t = Table.grid(padding=(0,1))
    t.add_column(style="magenta")
    t.add_column()
    
    def fmt_time(t_val):
        return f"{t_val:.2f}s" if isinstance(t_val, (int, float)) else str(t_val)
        
    t.add_row("Execution Time:", fmt_time(state.elapsed_time))
    t.add_row("Avg Step Time:", fmt_time(state.average_step_time))
    t.add_row("Fastest Step:", fmt_time(state.fastest_step))
    t.add_row("Slowest Step:", fmt_time(state.slowest_step))
    t.add_row("SQLite Latency:", f"{state.sqlite_latency:.2f}ms")
    
    layout.update(Panel(t, title="Performance", border_style="magenta"))

def _populate_recovery(layout: Layout, state: ConsoleState):
    t = Table.grid(padding=(0,1))
    t.add_column(style="red")
    t.add_column()
    
    t.add_row("Retries:", str(state.retries))
    t.add_row("Recoveries:", str(state.recoveries))
    t.add_row("Verify Fails:", str(state.verification_failures))
    t.add_row("Reflections:", str(state.reflection_decisions))
    t.add_row("Strategy:", state.current_recovery_strategy)
    
    layout.update(Panel(t, title="Recovery", border_style="red"))
    
def _populate_resources(layout: Layout, state: ConsoleState):
    t = Table.grid(padding=(0,1))
    t.add_column(style="yellow")
    t.add_column()
    
    t.add_row("CPU:", f"{state.cpu_percent}%")
    t.add_row("RAM:", f"{state.ram_percent}%")
    t.add_row("Threads:", str(state.thread_count))
    t.add_row("Workers:", str(state.worker_threads))
    
    layout.update(Panel(t, title="Resources", border_style="yellow"))

def _populate_timeline(layout: Layout, state: ConsoleState):
    t = Table(show_header=False, box=None)
    t.add_column(style="dim")
    t.add_column(style="bold white")
    
    # Reverse to show newest at top (or bottom, depending on preference)
    # Let's show newest at the bottom by iterating from max(0, len-20) to len
    events_to_show = list(state.events)[-25:]
    for timestamp, event in events_to_show:
        t.add_row(timestamp, event)
        
    layout.update(Panel(t, title="Event Timeline", border_style="white"))

def _populate_debug_state(layout: Layout, state: ConsoleState):
    stages = ["Planner", "Executor", "Reflection", "Recovery", "Verifier", "Completed"]
    
    group = []
    for stage in stages:
        if stage == state.active_stage:
            group.append(Text(f"→ {stage}", style="bold green reverse"))
        else:
            group.append(Text(f"  {stage}", style="dim"))
        if stage != stages[-1]:
            group.append(Text("  ↓", style="dim"))
            
    layout.update(Panel(Group(*group), title="Debug State", border_style="green"))
