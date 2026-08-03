import pytest
import tempfile
from jarvisx.capabilities.coding.pipeline.test_runner import TestRunner
from jarvisx.capabilities.coding.sandbox.sandbox_manager import SandboxManager

@pytest.mark.asyncio
async def test_test_runner_python_command():
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = SandboxManager(allowed_commands=["python"])
        runner = TestRunner(sandbox_manager=sandbox)

        res = await runner.run_tests(
            repo_path=tmpdir,
            test_command="python -c \"print('Tests passed')\""
        )

        assert res.passed is True
        assert res.passed_count >= 1
        assert "Tests passed" in res.stdout
