"""
Debug 3: Minimal inline trace to find exact fault-firing behavior.
No patching of time.sleep - just print what check_step_fault sees.
"""
import os, sys, time, sqlite3
from contextlib import closing

sys.path.insert(0, os.path.abspath("src"))

# Patch FaultInjector.check_step_fault BEFORE importing anything
from jarvisx.core.execution.fault_injector import FaultInjector

_orig_check_step = FaultInjector.check_step_fault
def _traced_check_step(self, context, action_type):
    result = _orig_check_step(self, context, action_type)
    print(f"  [check_step_fault] obj={context.objective_id} step={context.current_step} action={action_type} -> {'FAULT' if result else 'None'}", flush=True)
    return result
FaultInjector.check_step_fault = _traced_check_step

from jarvisx.core.execution.task_executor import TaskExecutor
_orig_execute_step = TaskExecutor._execute_step
def _traced_execute_step(self, step):
    print(f"  [_execute_step] action={step.get('action_type')} ctx_step={self.context.current_step}", flush=True)
    result = _orig_execute_step(self, step)
    print(f"  [_execute_step] RESULT={result[0]}", flush=True)
    return result
TaskExecutor._execute_step = _traced_execute_step

_orig_verify_step = TaskExecutor._verify_step
def _traced_verify_step(self, step):
    print(f"  [_verify_step] verif={step.get('verification')} target={step.get('verification_target')}", flush=True)
    result = _orig_verify_step(self, step)
    print(f"  [_verify_step] RESULT={result}", flush=True)
    return result
TaskExecutor._verify_step = _traced_verify_step

from jarvisx.tools.dev_console.app import ConsoleApp
from jarvisx.core.execution.persistent_queue import Priority
from jarvisx.core.voice.tts_engine import TTSEngine

TTSEngine.speak = lambda self, text: None
FaultInjector().clear()

db_path = f"debug3_{int(time.time())}.db"
app = ConsoleApp()
app.db_path = db_path
app.setup_engine()

folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Debug3")
os.makedirs(folder, exist_ok=True)

obj_id = f"dbg3_{int(time.time())}"
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

# Inject permanent fault at step_index=0 (the only step)
app.fault_injector.inject_step_fault(obj_id, "CREATE_FILE_DIRECT", 0, RuntimeError("Fault!"), max_triggers=-1)
print(f"Faults: {list(app.fault_injector._faults.keys())}", flush=True)
print(f"Executor injector is app injector: {app.executor.injector is app.fault_injector}", flush=True)

app.queue.enqueue(obj_id, "Debug single fault step", obj_data, Priority.NORMAL)

t0 = time.time()
app.worker.start()

# Let it run for 20 seconds (stop tracking)
time.sleep(20)
app.worker.stop()

with closing(sqlite3.connect(db_path)) as conn:
    row = conn.execute("SELECT status, current_step FROM objectives WHERE objective_id = ?", (obj_id,)).fetchone()
print(f"\nFinal status: {row}", flush=True)
print(f"Remaining faults: {list(app.fault_injector._faults.keys())}", flush=True)
