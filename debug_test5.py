"""
Debug 5: Print exact step dict when _verify_step is called.
"""
import os, sys, time, sqlite3, traceback as tb
from contextlib import closing

sys.path.insert(0, os.path.abspath("src"))

# Override check_step_fault to print each call
from jarvisx.core.execution.fault_injector import FaultInjector
_orig_csf = FaultInjector.check_step_fault
_N = [0]
def _csf(self, context, action_type):
    _N[0] += 1
    r = _orig_csf(self, context, action_type)
    print(f"[check_step_fault #{_N[0]}] step={context.current_step} action={action_type} -> {'FAULT' if r else 'None'}", flush=True)
    return r
FaultInjector.check_step_fault = _csf

# Completely replace _verify_step
from jarvisx.core.execution.task_executor import TaskExecutor
_orig_vs = TaskExecutor._verify_step
def _vs(self, step):
    print(f"\n=== _verify_step CALLED ===", flush=True)
    print(f"  step dict: {step}", flush=True)
    tb.print_stack()
    r = _orig_vs(self, step)
    print(f"  _verify_step result: {r}", flush=True)
    return r
TaskExecutor._verify_step = _vs

from jarvisx.tools.dev_console.app import ConsoleApp
from jarvisx.core.execution.persistent_queue import Priority
from jarvisx.core.voice.tts_engine import TTSEngine

TTSEngine.speak = lambda self, text: None
FaultInjector().clear()

db_path = f"debug5_{int(time.time())}.db"
app = ConsoleApp()
app.db_path = db_path
app.setup_engine()

folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Debug5")
os.makedirs(folder, exist_ok=True)

obj_id = f"dbg5_{int(time.time())}"
obj_data = {
    "objective_id": obj_id,
    "objective_type": "CREATE_FILES",
    "steps": [
        {
            "step_id": 1,
            "description": "Fault step",
            "action_type": "CREATE_FILE_DIRECT",
            "target": f"{folder}/fault.txt",
            "verification": "FILE_EXISTS",
            "verification_target": f"{folder}/fault.txt",
        }
    ],
}

app.fault_injector.inject_step_fault(obj_id, "CREATE_FILE_DIRECT", 0, RuntimeError("Fault!"), max_triggers=-1)
print(f"FaultInjector id: {id(app.executor.injector)} == {id(app.fault_injector)} : {app.executor.injector is app.fault_injector}", flush=True)
print(f"coordinator.verifier_fn = {app.executor.coordinator.verifier_fn}", flush=True)
print(f"executor._verify_step = {app.executor._verify_step}", flush=True)
print(f"Same? {app.executor.coordinator.verifier_fn is app.executor._verify_step}", flush=True)

app.queue.enqueue(obj_id, "Debug single fault step", obj_data, Priority.NORMAL)

app.worker.start()
time.sleep(12)
app.worker.stop()

with closing(sqlite3.connect(db_path)) as conn:
    row = conn.execute("SELECT status, current_step FROM objectives WHERE objective_id = ?", (obj_id,)).fetchone()
print(f"\nFinal: {row}", flush=True)
