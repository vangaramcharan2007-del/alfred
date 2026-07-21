"""
Debug 2: Add detailed timing to find exactly where the hang occurs.
"""
import os, sys, time, sqlite3, threading
from contextlib import closing

sys.path.insert(0, os.path.abspath("src"))

# Patch time.sleep to log calls
original_sleep = time.sleep
_sleep_count = [0]

def traced_sleep(secs):
    _sleep_count[0] += 1
    import traceback
    stack = ''.join(traceback.format_stack(limit=5))
    print(f"[SLEEP #{_sleep_count[0]}] {secs}s from:\n{stack}", flush=True)
    original_sleep(secs)

time.sleep = traced_sleep

from jarvisx.tools.dev_console.app import ConsoleApp
from jarvisx.core.execution.persistent_queue import Priority
from jarvisx.core.execution.fault_injector import FaultInjector
from jarvisx.core.voice.tts_engine import TTSEngine

TTSEngine.speak = lambda self, text: None
FaultInjector().clear()

db_path = f"debug2_{int(time.time())}.db"

app = ConsoleApp()
app.db_path = db_path
app.setup_engine()

desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Debug2")
os.makedirs(desktop_folder, exist_ok=True)

obj_id = f"dbg2_{int(time.time())}"
obj_data = {
    "objective_id": obj_id,
    "objective_type": "CREATE_FILES",
    "steps": [
        {
            "step_id": 1,
            "description": "Step 1",
            "action_type": "CREATE_FILE_DIRECT",
            "target": f"{desktop_folder}/file_1.txt",
            "verification": "FILE_EXISTS",
            "verification_target": f"{desktop_folder}/file_1.txt",
        },
        {
            "step_id": 2,
            "description": "Fault step",
            "action_type": "CREATE_FILE_DIRECT",
            "target": f"{desktop_folder}/file_2.txt",
            "verification": "FILE_EXISTS",
            "verification_target": f"{desktop_folder}/file_2.txt",
        },
    ],
}

# Inject permanent fault at step 1 (0-based = 2nd step)
app.fault_injector.inject_step_fault(obj_id, "CREATE_FILE_DIRECT", 1, RuntimeError("Fault!"), max_triggers=-1)
app.queue.enqueue(obj_id, "Debug 2-step obj", obj_data, Priority.NORMAL)

t0 = time.time()
app.worker.start()

# Poll for 25 seconds
for _ in range(25):
    original_sleep(1)
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute("SELECT status, current_step FROM objectives WHERE objective_id = ?", (obj_id,)).fetchone()
    print(f"[t={time.time()-t0:.0f}s] status={row[0] if row else '?'} step={row[1] if row else '?'}", flush=True)
    if row and row[0] in ("FAILED", "COMPLETED"):
        break

app.worker.stop()
print(f"FINAL: {app.queue.get_all_by_status([]) if False else 'done'}", flush=True)
with closing(sqlite3.connect(db_path)) as conn:
    row = conn.execute("SELECT status, current_step FROM objectives WHERE objective_id = ?", (obj_id,)).fetchone()
print(f"Final status: {row}", flush=True)
print(f"Total traced sleeps: {_sleep_count[0]}", flush=True)
