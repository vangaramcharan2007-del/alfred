import pytest
from pathlib import Path
from jarvisx.tools.memory import LocalMemoryTool

def test_integration_memory_persistence():
    tool = LocalMemoryTool(vault_path=Path("var/test_vault"))
    res = tool.save_memory("test_key: content_persistent", "general")
    assert res.success is True

    found = tool.search_memory("content_persistent")
    assert found.success is True
    records = found.data.get("records", []) or found.data.get("results", [])
    assert len(records) > 0
