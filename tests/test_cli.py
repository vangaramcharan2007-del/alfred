from jarvisx.interface.cli import JarvisCLI
from jarvisx.kernel.runtime_kernel import RuntimeKernel

def test_cli_commands():
    kernel = RuntimeKernel()
    cli = JarvisCLI(kernel=kernel)

    help_res = cli.handle_command("help")
    assert "commands" in help_res
    assert "status" in help_res["commands"]

    status_res = cli.handle_command("status")
    assert "runtime" in status_res
    assert "health" in status_res

    mission_res = cli.handle_command('mission "build AI app"')
    assert mission_res["action"] == "mission"

    evolve_res = cli.handle_command("evolve")
    assert evolve_res["action"] == "evolve"

    unknown_res = cli.handle_command("foobar")
    assert "error" in unknown_res
