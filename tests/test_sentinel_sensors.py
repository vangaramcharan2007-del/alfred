import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from scripts.auto_wake_sentinel import is_workstation_locked, is_lockscreen_open

class TestSentinelSensors(unittest.TestCase):
    def test_workstation_locked_type(self):
        locked = is_workstation_locked()
        self.assertIsInstance(locked, bool)
        print(f"\n[SENSOR TEST] Current workstation locked status: {locked}")

    def test_lockscreen_open_type(self):
        is_open = is_lockscreen_open()
        self.assertIsInstance(is_open, bool)
        print(f"[SENSOR TEST] Naruto Live Lock Screen currently open: {is_open}")

if __name__ == "__main__":
    unittest.main()
