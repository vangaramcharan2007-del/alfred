import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from jarvisx.tools.operational_db import OperationalDatabase
from jarvisx.clients.supabase_client import SupabaseClient


class TestOperationalDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_op.db"
        
        # Mock Supabase
        self.mock_supabase = MagicMock(spec=SupabaseClient)
        self.mock_supabase.is_configured = True
        self.mock_supabase.insert.return_value = (True, {})
        
        self.op_db = OperationalDatabase(self.db_path, supabase=self.mock_supabase)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_set_and_get(self) -> None:
        # Prevent background sync thread from locking the DB on Windows
        self.op_db._trigger_sync = MagicMock()
        
        # Test basic SQLite operation
        self.op_db.set("test_key", {"foo": "bar"})
        data = self.op_db.get("test_key")
        self.assertIsNotNone(data)
        self.assertEqual(data["foo"], "bar")

    def test_sync_trigger(self) -> None:
        # Test if sync is called
        self.op_db.set("sync_key", {"a": 1})
        
        # Wait slightly for background thread (not ideal but works for simple tests)
        import time
        time.sleep(0.1)
        
        self.mock_supabase.insert.assert_called_with("operational_data", {"id": "sync_key", "data": {"a": 1}})
        
        # Verify it was marked as synced
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT synced FROM operational_data WHERE key = 'sync_key'").fetchone()
        self.assertEqual(row["synced"], 1)
        conn.close()


if __name__ == "__main__":
    unittest.main()
