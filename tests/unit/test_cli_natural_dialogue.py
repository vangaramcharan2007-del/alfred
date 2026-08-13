"""Unit test verifying natural language greetings and conversational handling in JarvisCLI."""

import pytest
from unittest.mock import MagicMock

from jarvisx.interface.cli import JarvisCLI
from jarvisx.kernel.runtime_kernel import RuntimeKernel


@pytest.mark.asyncio
async def test_cli_handles_greetings_and_casual_queries():
    kernel = MagicMock()
    kernel.health_check.return_value = {"overall": "HEALTHY", "health_score": 100, "online": True}
    cli = JarvisCLI(kernel=kernel)

    # 1. Test "hi" greeting
    res_hi = await cli.handle_command_async("hi")
    assert res_hi["status"] == "SUCCESS"
    assert "Hello" in res_hi["output"]
    assert "Alfred" in res_hi["output"]

    # 2. Test "hloo" greeting
    res_hloo = await cli.handle_command_async("hloo")
    assert res_hloo["status"] == "SUCCESS"
    assert "Hello" in res_hloo["output"]

    # 3. Test "wdym" query
    res_wdym = await cli.handle_command_async("wdym")
    assert res_wdym["status"] == "SUCCESS"
    assert "personal AI" in res_wdym["output"]

    # 4. Test "what time is it"
    res_time = await cli.handle_command_async("what time is it")
    assert res_time["status"] == "SUCCESS"
    assert "time is" in res_time["output"]
