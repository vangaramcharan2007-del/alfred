"""Replay mode for the Jarvis X Developer Console."""
import os
import json
import time
from rich.live import Live

from jarvisx.core.execution.event_bus import ExecutionEvent
from jarvisx.tools.dev_console.state import ConsoleState
from jarvisx.tools.dev_console.dashboard import generate_layout

class ConsoleReplay:
    """Replays an execution session strictly from recorded EventBus events."""

    @staticmethod
    def prompt_and_replay(state: ConsoleState):
        """Prompt user to replay the current or a past session."""
        print("\nReplay Mode: Do you want to replay a session? (y/N)")
        ans = input("> ").strip().lower()
        if ans == 'y':
            sessions_dir = os.path.join("logs", "sessions")
            if not os.path.exists(sessions_dir):
                print("No sessions found.")
                return
            
            files = sorted([f for f in os.listdir(sessions_dir) if f.endswith(".json")], reverse=True)
            if not files:
                print("No session JSON files found.")
                return
                
            print("\nAvailable Sessions:")
            for i, f in enumerate(files[:5]):
                print(f"{i+1}) {f}")
                
            ans = input(f"\nSelect session [1-{min(5, len(files))}]: ").strip()
            try:
                idx = int(ans) - 1
                if 0 <= idx < len(files):
                    ConsoleReplay.replay_session(os.path.join(sessions_dir, files[idx]))
            except ValueError:
                pass

    @staticmethod
    def replay_session(json_path: str):
        """Reconstruct the Dashboard visually purely from the JSON event timeline."""
        if not os.path.exists(json_path):
            print(f"File not found: {json_path}")
            return
            
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        print(f"\nReplaying Session: {os.path.basename(json_path)}")
        time.sleep(1)
        
        state = ConsoleState()
        # Initialize state with recorded objective data
        obj_data = data.get("objective", {})
        state.objective_id = obj_data.get("id", "")
        state.objective_name = obj_data.get("name", "")
        state.total_steps = obj_data.get("total_steps", 0)
        
        timeline = data.get("timeline", [])
        
        # We simulate the passing of events over time
        
        try:
            with Live(generate_layout(state, None), refresh_per_second=10) as live:
                for timestamp_str, event_name in timeline:
                    # Parse Event enum by name if possible, though our state only needs names
                    # We just need to feed it back to event listener?
                    # Event Listener expects the actual ExecutionEvent enum and payload.
                    # Since our log only has (timestamp, event_name), we can either:
                    # 1) Try to reconstruct payload (hard)
                    # 2) Just push the event string directly to timeline and increment counts based on event.
                    
                    state.add_event(event_name)
                    
                    with state.lock:
                        if event_name == "OBJECTIVE_STARTED":
                            state.objective_status = "RUNNING"
                            state.set_active_stage("Planner")
                        elif event_name == "STEP_STARTED":
                            state.current_step = min(state.current_step + 1, state.total_steps)
                            state.remaining_steps = max(0, state.total_steps - state.current_step)
                            state.set_active_stage("Executor")
                        elif event_name == "VERIFICATION_STARTED":
                            state.set_active_stage("Verifier")
                        elif event_name == "VERIFICATION_FAILED":
                            state.verification_failures += 1
                            state.set_active_stage("Reflection")
                        elif event_name == "STEP_FAILED":
                            state.set_active_stage("Reflection")
                        elif event_name == "RECOVERY_STARTED":
                            state.set_active_stage("Recovery")
                        elif event_name == "RECOVERY_SUCCEEDED":
                            state.recoveries += 1
                            state.retries += 1
                            state.set_active_stage("Executor")
                        elif event_name == "OBJECTIVE_CHECKPOINT_SAVED":
                            state.checkpoint_index = state.current_step
                        elif event_name == "BACKGROUND_WORKER_STARTED":
                            state.worker_status = "ACTIVE"
                        elif event_name == "BACKGROUND_WORKER_STOPPED":
                            state.worker_status = "STOPPED"
                        elif event_name == "OBJECTIVE_COMPLETED":
                            state.objective_status = "COMPLETED"
                            state.set_active_stage("Completed")
                        elif event_name == "OBJECTIVE_FAILED":
                            state.objective_status = "FAILED"
                            state.set_active_stage("Completed")
                            
                    live.update(generate_layout(state, None))
                    time.sleep(0.05) # Speed up replay 
                    
        except KeyboardInterrupt:
            pass
            
        print("\nReplay finished.")
