"""
Debug 4: Trace the full call stack when _verify_step is called after a fault.
"""
import os, sys, time, sqlite3, traceback
from contextlib import closing

sys.path.insert(0, os.path.abspath("src"))

from jarvisx.core.execution.fault_injector import FaultInjector

_orig_check_step = FaultInjector.check_step_fault
_call_count = [0]

def _traced_check_step(self, context, action_type):
    result = _orig_check_step(self, context, action_type)
    _call_count[0] += 1
    print(f"  [check_step_fault #{_call_count[0]}] step={context.current_step} -> {'FAULT' if result else 'None'}", flush=True)
    return result
FaultInjector.check_step_fault = _traced_check_step

from jarvisx.core.execution.task_executor import TaskExecutor

_orig_verify = TaskExecutor._verify_step
def _traced_verify(self, step):
    print(f"\n!!! _verify_step CALLED !!!", flush=True)
    print("Stack trace:", flush=True)
    traceback.print_stack()
    result = _orig_verify(self, step)
    return result
TaskExecutor._verify_step = _traced_verify

from jarvisx.tools.dev_console.app import ConsoleApp
from jarvisx.core.execution.persistent_queue import Priority
from jarvisx.core.voice.tts_engine import TTSEngine

TTSEngine.speak = lambda self, text: None
FaultInjector().clear()

db_path = f"debug4_{int(time.time())}.db"
app = ConsoleApp()
app.db_path = db_path
app.setup_engine()

folder = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Debug4")
os.makedirs(folder, exist_ok=True)

obj_id = f"dbg4_{int(time.time())}"
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
print(f"injector id: {id(app.executor.injector)} == {id(app.fault_injector)}: {app.executor.injector is app.fault_injector}", flush=True)

app.queue.enqueue(obj_id, "Debug single fault step", obj_data, Priority.NORMAL)

app.worker.start()
time.sleep(15)
app.worker.stop()

with closing(sqlite3.connect(db_path)) as conn:
    row = conn.execute("SELECT status, current_step FROM objectives WHERE objective_id = ?", (obj_id,)).fetchone()
print(f"\nFinal: {row}", flush=True)
