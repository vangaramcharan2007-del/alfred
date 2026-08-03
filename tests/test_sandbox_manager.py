import pytest
import asyncio
from jarvisx.capabilities.coding.sandbox.sandbox_manager import SandboxManager, SandboxSecurityError

@pytest.mark.asyncio
async def test_sandbox_allowlist_validation():
    sandbox = SandboxManager(allowed_commands=["python", "pytest", "echo"])
    
    assert sandbox.validate_command("python script.py") == "python"
    assert sandbox.validate_command("echo Hello") == "echo"

    with pytest.raises(SandboxSecurityError):
        sandbox.validate_command("rm -rf /")

@pytest.mark.asyncio
async def test_sandbox_execution_success():
    sandbox = SandboxManager(allowed_commands=["python"])
    res = await sandbox.execute_command("python -c \"print('Sandbox active')\"")
    assert res["exit_code"] == 0
    assert "Sandbox active" in res["stdout"]

@pytest.mark.asyncio
async def test_sandbox_execution_timeout():
    sandbox = SandboxManager(allowed_commands=["python"], default_timeout_seconds=0.5)
    res = await sandbox.execute_command("python -c \"import time; time.sleep(2)\"")
    assert res["timed_out"] is True
    assert res["exit_code"] == -1
