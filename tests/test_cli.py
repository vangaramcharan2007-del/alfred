import pytest
from jarvisx.interface.cli import JarvisCLI
from jarvisx.kernel.runtime_kernel import RuntimeKernel

def test_cli_sync_commands():
    kernel = RuntimeKernel()
    cli = JarvisCLI(kernel=kernel)

    help_res = cli.handle_command("help")
    assert "commands" in help_res
    assert "status" in help_res["commands"]

    status_res = cli.handle_command("status")
    assert "system_health" in status_res
    assert "active_agents" in status_res
    assert "models_available" in status_res
    assert "memory_size" in status_res
    assert "evolution_level" in status_res

    mission_res = cli.handle_command('mission "build AI app"')
    assert mission_res["action"] == "mission"

    evolve_res = cli.handle_command("evolve")
    assert evolve_res["action"] == "evolve"

    unknown_res = cli.handle_command("foobar")
    assert "error" in unknown_res

@pytest.mark.asyncio
async def test_cli_async_commands():
    kernel = RuntimeKernel()
    await kernel.boot()
    cli = JarvisCLI(kernel=kernel)

    mission_res = await cli.handle_command_async('mission "build AI app"')
    assert mission_res["status"] == "COMPLETED"
    assert mission_res["mission_result"]["mission"]["status"] == "COMPLETED"

    evolve_res = await cli.handle_command_async("evolve")
    assert evolve_res["status"] == "COMPLETED"
