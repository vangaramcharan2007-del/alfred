"""
Quick debug: what status does the objective actually reach?
Run: python debug_test.py
"""
import os
import sys
import time
import sqlite3
from contextlib import closing

sys.path.insert(0, os.path.abspath("src"))

from jarvisx.tools.dev_console.app import ConsoleApp
from jarvisx.core.execution.persistent_queue import Priority
from jarvisx.core.execution.fault_injector import FaultInjector
from jarvisx.core.voice.tts_engine import TTSEngine
import logging

# Enable logging so we can see what's happening
logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")

TTSEngine.speak = lambda self, text: None

print("=== TEST: Fault injection scenario ===")

FaultInjector().clear()
db_path = f"debug_{int(time.time())}.db"

app1 = ConsoleApp()
app1.db_path = db_path
app1.setup_engine()

desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Debug")
os.makedirs(desktop_folder, exist_ok=True)

obj_id = f"debug_{int(time.time())}"
obj_data = {
    "objective_id": obj_id,
    "objective_type": "CREATE_FILES",
    "steps": [
        {
            "step_id": i,
            "description": f"Create file_{i}.txt",
            "action_type": "CREATE_FILE_DIRECT",
            "target": f"{desktop_folder}/file_{i}.txt",
            "verification": "FILE_EXISTS",
            "verification_target": f"{desktop_folder}/file_{i}.txt",
        }
        for i in range(1, 6)
    ],
}

print(f"Objective ID: {obj_id}")
print(f"Injecting fault at step_index=2 (3rd step, 0-based), max_triggers=-1")
app1.fault_injector.inject_step_fault(obj_id, "CREATE_FILE_DIRECT", 2, RuntimeError("Debug crash"), max_triggers=-1)

print(f"Faults registered: {list(app1.fault_injector._faults.keys())}")
print(f"Executor injector id: {id(app1.executor.injector)}")
print(f"App fault_injector id: {id(app1.fault_injector)}")
print(f"Same object: {app1.executor.injector is app1.fault_injector}")

app1.queue.enqueue(obj_id, "Debug 5 files", obj_data, Priority.NORMAL)

t0 = time.time()
app1.worker.start()

print("Worker started. Polling for status...")
for _ in range(30):
    time.sleep(1)
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute(
            "SELECT status, current_step FROM objectives WHERE objective_id = ?", (obj_id,)
        ).fetchone()
    print(f"  t={time.time()-t0:.0f}s: status={row[0] if row else 'N/A'}, step={row[1] if row else '?'}")
    if row and row[0] in ("FAILED", "COMPLETED"):
        print(f"  => Reached terminal state: {row[0]}")
        break

app1.worker.stop()

with closing(sqlite3.connect(db_path)) as conn:
    row = conn.execute(
        "SELECT status, current_step FROM objectives WHERE objective_id = ?", (obj_id,)
    ).fetchone()
    faults_remaining = list(app1.fault_injector._faults.keys())

print(f"\nFinal status: {row}")
print(f"Remaining faults: {faults_remaining}")
