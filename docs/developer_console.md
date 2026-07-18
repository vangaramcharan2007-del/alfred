# Jarvis X Developer Console

The Jarvis X Developer Console is the permanent observability, validation, and debugging environment for the execution engine. It directly hooks into the production pipeline (acting as a pure observer and command router) and presents a robust Text User Interface (TUI) via `rich`.

## Architecture
The console is built in `src/jarvisx/tools/dev_console/`:
- `app.py`: Entry point and orchestrator.
- `dashboard.py`: Contains `rich` layout definitions.
- `event_listener.py`: Captures EventBus emissions and translates them into UI state.
- `command_router.py`: Non-blocking daemon handling user input (`msvcrt`).
- `metrics.py`: Analyzes database latencies and queries system utilization (`psutil`).
- `session_logger.py`: Auto-dumps complete session execution traces (timelines, logs, metrics) to `logs/sessions/`.
- `replay.py`: Reads the captured event timeline and streams it chronologically to the console.

## The Dashboard Panels
- **Live Dashboard**: Real-time progress bar, target information, and checkpoint status.
- **Event Timeline**: A scrolling list of the last 100 system events (e.g., `OBJECTIVE_STARTED`, `RECOVERY_STARTED`).
- **Resource Monitoring**: Live CPU/RAM/Thread allocation (gracefully degrades if `psutil` is uninstalled).
- **Recovery Diagnostics**: Tracks automated reflection decisions, retries, and alternate tool successes.
- **Performance Diagnostics**: Measures execution speeds and component latency.
- **Debug State Tracker**: Graphically highlights exactly which engine component (Planner -> Executor -> Reflection -> Verifier) is currently active.

## Keyboard Shortcuts
Use these hotkeys at any time without pressing Enter:
- `P`: Pause execution
- `R`: Resume execution
- `C`: Simulate a hard process crash (immediately flushing state to SQLite and terminating the worker)
- `X`: Cancel active objective
- `S`: Dump statistics
- `E`: Export session diagnostic
- `L`: Replay Timeline
- `H`: Help
- `Q`: Quit

## Usage
Simply run:
```bash
python src/jarvisx/tools/dev_console/app.py
```
On startup, you can inject a fault mode (e.g. `Missing Browser` or `Permission Error`). The console will then seamlessly execute the queued objectives in the background while keeping you deeply informed of every micro-decision the autonomous engine makes.
