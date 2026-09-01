"""
Unit tests for the Ultimate 5-Pillar Sovereign Linux Suite in Jarvis X / Alfred OS.
"""

import pytest
from jarvisx.agents.linux_agent import LinuxBridgeAgent
from jarvisx.agents.linux_devops import LinuxDevOpsOrchestrator
from jarvisx.agents.linux_ai_sandbox import LinuxAISandbox
from jarvisx.agents.linux_cyber_sentinel import LinuxCyberSentinel
from jarvisx.agents.linux_shadow_worker import LinuxShadowWorker
from jarvisx.agents.linux_binary_toolchain import LinuxBinaryToolchain
from jarvisx.tools.tool_kernel import ToolRegistry
from jarvisx.tools.builtin_tools import (
    register_builtin_tools,
    ManageLinuxServiceTool,
    RunLinuxAITrainingTool,
    ScanLinuxNetworkSecurityTool,
    DispatchLinuxShadowTaskTool,
    CompileLinuxSourceTool,
)


def test_devops_orchestrator_lifecycle():
    devops = LinuxDevOpsOrchestrator.get_instance()
    
    # Start service
    start_res = devops.start_service("TestAPI", 8088, "python3 -m http.server 8088")
    assert start_res["status"] in ("success", "already_running")
    assert start_res["port"] == 8088

    # List services
    services = devops.list_services()
    assert any(s["name"] == "TestAPI" for s in services)

    # Stop service
    stop_res = devops.stop_service("TestAPI")
    assert stop_res["status"] == "success"


def test_ai_sandbox_training_and_benchmark():
    ai_box = LinuxAISandbox.get_instance()
    
    # Train
    train_res = ai_box.run_training_pipeline(dataset_name="sih_vision_data", model_architecture="Transformer-Mini", epochs=5)
    assert train_res["status"] == "completed"
    assert train_res["accuracy_pct"] > 50.0

    # Benchmark
    bench_res = ai_box.benchmark_inference("Jarvis-Edge-V1", batch_size=64)
    assert bench_res["status"] == "success"
    assert bench_res["throughput_items_per_sec"] > 0


def test_cyber_sentinel_network_and_code_audit(tmp_path):
    sentinel = LinuxCyberSentinel.get_instance()
    
    # Network scan
    net_res = sentinel.scan_local_network([80, 443])
    assert net_res["status"] == "success"
    assert "local_ip" in net_res

    # Code audit on clean folder
    audit_clean = sentinel.audit_code_security(str(tmp_path))
    assert audit_clean["status"] == "success"
    assert audit_clean["total_vulnerabilities"] == 0

    # Code audit with injected test pattern
    test_file = tmp_path / "vulnerable_test.py"
    test_file.write_text("api_key = 'abcdef12345678901234567890'\neval('2+2')\n")
    audit_injected = sentinel.audit_code_security(str(tmp_path))
    assert audit_injected["total_vulnerabilities"] >= 2


def test_shadow_worker_dispatch():
    worker = LinuxShadowWorker.get_instance()
    res = worker.dispatch_task("DataCleanJob", "for i in 1 2 3; do echo $i; done")
    assert res["status"] == "success"
    assert res["worker_status"] == "completed"

    tasks = worker.list_active_tasks()
    assert len(tasks) > 0


def test_binary_toolchain_compile_and_inspect():
    toolchain = LinuxBinaryToolchain.get_instance()
    
    # Compile C
    c_code = "#include <stdio.h>\nint main() { printf(\"Jarvis Linux Core\\n\"); return 0; }"
    compile_res = toolchain.compile_source(c_code, language="c", output_name="jarvis_core.out")
    assert compile_res["status"] == "success"
    assert compile_res["output_binary"] != ""

    # Inspect
    inspect_res = toolchain.inspect_binary(compile_res["output_binary"])
    assert inspect_res["status"] == "success"
    assert inspect_res["architecture"] == "x86_64"


def test_builtin_tools_suite_registration():
    registry = ToolRegistry.get_instance()
    register_builtin_tools(registry)

    # 1. ManageLinuxServiceTool
    srv_tool = registry.get("manage_linux_service")
    assert srv_tool is not None
    assert srv_tool.execute({"action": "list"}).status == "success"

    # 2. RunLinuxAITrainingTool
    ai_tool = registry.get("run_linux_ai_training")
    assert ai_tool is not None
    assert ai_tool.execute({"epochs": 3}).status == "success"

    # 3. ScanLinuxNetworkSecurityTool
    sec_tool = registry.get("scan_linux_network_security")
    assert sec_tool is not None
    assert sec_tool.execute({"scan_type": "network"}).status == "success"

    # 4. DispatchLinuxShadowTaskTool
    shadow_tool = registry.get("dispatch_linux_shadow_task")
    assert shadow_tool is not None
    assert shadow_tool.execute({"task_name": "UnitTestTask", "command": "echo OK"}).status == "success"

    # 5. CompileLinuxSourceTool
    compile_tool = registry.get("compile_linux_source")
    assert compile_tool is not None
    assert compile_tool.execute({"source_code": "int main() { return 0; }", "language": "c"}).status == "success"
