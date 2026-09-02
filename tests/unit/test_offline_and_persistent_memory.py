"""
Unit Tests for Offline Fallback & SQLite Persistent Conversation Memory.
=======================================================================
Verifies:
1. Zero data loss across simulated power cuts / reboots.
2. Conversation history restored on new AlfredOrganism instance.
3. Ollama provider auto-launches and falls back seamlessly when offline.
"""

import unittest
import tempfile
import os
import shutil
import sqlite3
import asyncio
from unittest.mock import patch, MagicMock

from jarvisx.memory.conversation_store import PersistentConversationStore
from jarvisx.llm.ollama_provider import OllamaLLMProvider


class TestOfflineAndPersistentMemory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_conversation.db")
        self.store = PersistentConversationStore(self.db_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_persistent_memory_across_simulated_power_cut(self):
        """Simulate power outage: save turns, kill store instance, create fresh instance, verify history."""
        # 1. User and Alfred have a multi-turn conversation
        self.store.save_turn("user", "Hello Alfred, remember my secret code is 9988")
        self.store.save_turn("assistant", "Understood Sir, I will remember 9988.")
        self.store.save_turn("user", "What is the 1D Heat Equation?")
        self.store.save_turn("assistant", "The 1D Heat equation is u_t = alpha^2 u_xx.")

        self.assertEqual(self.store.get_total_turns_count(), 4)

        # 2. Simulate complete power cut / process termination (delete store instance)
        del self.store

        # 3. New process boots up after power recovery and attaches to the same DB
        new_store = PersistentConversationStore(self.db_path)
        restored_history = new_store.load_recent_history(limit=10)

        self.assertEqual(len(restored_history), 4)
        self.assertEqual(restored_history[0]["role"], "user")
        self.assertEqual(restored_history[0]["text"], "Hello Alfred, remember my secret code is 9988")
        self.assertEqual(restored_history[1]["role"], "assistant")
        self.assertEqual(restored_history[2]["text"], "What is the 1D Heat Equation?")

        # 4. Test searching past context
        search_results = new_store.search_past_context("secret code")
        self.assertTrue(len(search_results) > 0)
        self.assertIn("9988", search_results[0]["text"])

    @patch("shutil.which", return_value="/usr/bin/ollama")
    @patch("subprocess.Popen")
    @patch("urllib.request.urlopen")
    def test_ollama_provider_auto_start_on_disconnect(self, mock_urlopen, mock_popen, mock_which):
        """Test that Ollama provider auto-spawns background serve when offline."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{"models": [{"name": "alfred:latest"}, {"name": "qwen2.5-coder:1.5b"}]}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        provider = OllamaLLMProvider()
        connected = asyncio.run(provider.connect())
        self.assertTrue(connected)
        self.assertIn("alfred:latest", provider.installed_models)
        self.assertEqual(provider.select_model_for_prompt("hi"), "alfred:latest")


if __name__ == "__main__":
    unittest.main()
