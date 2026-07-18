import os
import unittest
from typing import Dict, Any

from jarvisx.core.execution.event_bus import EventBus, ExecutionEvent
from jarvisx.core.execution.execution_context import ExecutionContext
from jarvisx.core.execution.capability_registry import CapabilityRegistry, Capability
from jarvisx.core.execution.failure_classifier import FailureClassifier, FailureCategory
from jarvisx.core.execution.reflection_engine import ReflectionEngine, ReflectionResult
from jarvisx.core.execution.recovery_planner import RecoveryPlanner, RecoveryStrategy
from jarvisx.core.execution.execution_coordinator import ExecutionCoordinator

class TestPhase22(unittest.TestCase):
    
    def test_event_bus(self):
        bus = EventBus()
        events_received = []
        
        def callback(evt, payload):
            events_received.append((evt, payload))
            
        bus.subscribe(ExecutionEvent.STEP_STARTED, callback)
        bus.publish(ExecutionEvent.STEP_STARTED, {"test": "payload"})
        
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0][0], ExecutionEvent.STEP_STARTED)
        self.assertEqual(events_received[0][1]["test"], "payload")
        
        bus.unsubscribe(ExecutionEvent.STEP_STARTED, callback)
        bus.publish(ExecutionEvent.STEP_STARTED, {"test": "payload2"})
        self.assertEqual(len(events_received), 1)

    def test_execution_context(self):
        ctx = ExecutionContext()
        resolved_desktop = ctx.resolve_path("${DESKTOP}/file.txt")
        self.assertTrue(resolved_desktop.endswith("Desktop/file.txt") or resolved_desktop.endswith("Desktop\\file.txt"))
        
        ctx.register_placeholder("FOO", lambda: "/bar")
        resolved_custom = ctx.resolve_path("${FOO}/baz")
        self.assertEqual(resolved_custom, "/bar/baz")

    def test_capability_registry(self):
        reg = CapabilityRegistry()
        cap = reg.get("chrome")
        self.assertIsNotNone(cap)
        self.assertIn("edge", cap.alternatives)
        
        alts = reg.get_alternatives("chrome")
        self.assertEqual(alts, ["edge", "firefox"])

    def test_failure_classifier(self):
        cls = FailureClassifier()
        # Missing App
        cat = cls.classify("OPEN_APPLICATION", "fakeapp", FileNotFoundError("no such file"))
        self.assertEqual(cat, FailureCategory.MISSING_APPLICATION)
        
        # Missing File
        cat = cls.classify("TYPE_TEXT", "fakefile", FileNotFoundError("no such file"))
        self.assertEqual(cat, FailureCategory.MISSING_FILE)
        
        # Permission Denied
        cat = cls.classify("CREATE_FILE", "somepath", PermissionError("permission denied"))
        self.assertEqual(cat, FailureCategory.PERMISSION_DENIED)
        
        # Timeout
        cat = cls.classify("WAIT", "target", TimeoutError("timeout"))
        self.assertEqual(cat, FailureCategory.TIMEOUT)
        
        # Verification Mismatch
        cat = cls.classify("CLICK", "target", None, verification_failed=True)
        self.assertEqual(cat, FailureCategory.VERIFICATION_MISMATCH)

    def test_reflection_engine(self):
        ref = ReflectionEngine()
        
        # Success
        res = ref.reflect({"action_type": "CLICK"}, True, True, None)
        self.assertTrue(res.success)
        
        # App Missing
        res = ref.reflect({"action_type": "OPEN_APPLICATION", "target": "chrome"}, False, False, FileNotFoundError())
        self.assertFalse(res.success)
        self.assertTrue(res.recoverable)
        self.assertEqual(res.recommendation, "alternative_tool")
        
        # Permission Denied
        res = ref.reflect({"action_type": "CREATE_FILE"}, False, False, PermissionError())
        self.assertEqual(res.recommendation, "permission_recovery")

    def test_recovery_planner(self):
        reg = CapabilityRegistry()
        planner = RecoveryPlanner(reg)
        
        # Mock step and context
        step = {"action_type": "OPEN_APPLICATION", "target": "safari"}
        reg.register(Capability(name="safari", description="", alternatives=["edge"]))
        
        res = ReflectionResult(success=False, recoverable=True, failure_category=FailureCategory.MISSING_APPLICATION, recommendation="alternative_tool")
        
        called_targets = []
        def mock_executor(s):
            called_targets.append(s["target"])
            return True
            
        context = {"executor_fn": mock_executor}
        
        recovered = planner.plan_and_recover(res, step, context)
        self.assertTrue(recovered)
        self.assertIn("edge", called_targets)
        
    def test_execution_coordinator(self):
        bus = EventBus()
        ref = ReflectionEngine()
        plan = RecoveryPlanner(CapabilityRegistry())
        
        fail_count = [0]
        
        def mock_exec(s):
            if fail_count[0] == 0:
                fail_count[0] += 1
                return False, FileNotFoundError()
            return True, None
            
        def mock_verif(s):
            return True
            
        coord = ExecutionCoordinator(bus, ref, plan, mock_exec, mock_verif)
        
        # We try to open an app. First time fails, recovery kicks in.
        step = {"action_type": "OPEN_APPLICATION", "target": "chrome"}
        success = coord.coordinate_step(step)
        
        self.assertTrue(success)
        self.assertEqual(step["target"], "edge") # Modified by recovery

if __name__ == '__main__':
    unittest.main()
