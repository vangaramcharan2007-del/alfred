import os
import pytest
from jarvisx.core.tools.execution import (
    CommandExecutor,
    AppLauncher,
    FileOps,
    PythonExecutor,
    GitOps,
    PermissionManager,
    TrustLevel
)

def test_file_operations(tmp_path):
    test_file = str(tmp_path / "test.txt")
    assert FileOps.create_file(test_file, "content") == True
    assert FileOps.read_file(test_file) == "content"
    assert FileOps.delete_file(test_file) == True
    assert not os.path.exists(test_file)

def test_command_executor():
    # Windows native ping or echo
    res = CommandExecutor.execute("echo hello")
    assert res["success"] == True
    assert "hello" in res["stdout"].lower()

def test_python_executor():
    res = PythonExecutor.execute('print("hello world")')
    assert res["success"] == True
    assert "hello world" in res["stdout"].lower()

def test_permissions():
    PermissionManager.set_level(TrustLevel.LEVEL_0_READONLY)
    with pytest.raises(PermissionError):
        CommandExecutor.execute("echo hello")
    
    # Restore for other tests
    PermissionManager.set_level(TrustLevel.LEVEL_5_ADMIN)
