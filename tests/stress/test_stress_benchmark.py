import json
import time
import pytest
from pathlib import Path
from jarvisx.runtime.runtime import JarvisRuntime

BENCHMARK_TASKS = [
    # Beginner (8)
    {"id": 1, "category": "Beginner", "request": "Create password generator CLI"},
    {"id": 2, "category": "Beginner", "request": "Convert CSV to JSON tool"},
    {"id": 3, "category": "Beginner", "request": "Build markdown parser"},
    {"id": 4, "category": "Beginner", "request": "Create a string utility library"},
    {"id": 5, "category": "Beginner", "request": "Create a TODO CLI app"},
    {"id": 6, "category": "Beginner", "request": "Build a random number generator"},
    {"id": 7, "category": "Beginner", "request": "Create a file hasher utility"},
    {"id": 8, "category": "Beginner", "request": "Create a URL validator tool"},

    # Intermediate (6)
    {"id": 9, "category": "Intermediate", "request": "Add authentication to existing API"},
    {"id": 10, "category": "Intermediate", "request": "Optimize slow Python function"},
    {"id": 11, "category": "Intermediate", "request": "Add database storage layer"},
    {"id": 12, "category": "Intermediate", "request": "Create a JWT token service"},
    {"id": 13, "category": "Intermediate", "request": "Build an event emitter class"},
    {"id": 14, "category": "Intermediate", "request": "Create an HTTP client wrapper"},

    # Advanced (6)
    {"id": 15, "category": "Advanced", "request": "Analyze unfamiliar repository"},
    {"id": 16, "category": "Advanced", "request": "Refactor architecture"},
    {"id": 17, "category": "Advanced", "request": "Find security issue in module"},
    {"id": 18, "category": "Advanced", "request": "Upgrade dependencies and test compatibility"},
    {"id": 19, "category": "Advanced", "request": "Build an asynchronous worker queue"},
    {"id": 20, "category": "Advanced", "request": "Generate project technical documentation"}
]

@pytest.mark.asyncio
@pytest.mark.parametrize("task_info", BENCHMARK_TASKS)
async def test_20_task_stress_benchmark(task_info):
    runtime = JarvisRuntime()
    await runtime.start(print_banner=False)

    start_t = time.time()
    res = await runtime.process_task(task_info["request"])
    duration = round(time.time() - start_t, 3)

    assert res["status"] == "COMPLETED"
    result = res["mission_result"]["result"]

    files = result["files_changed"]
    assert len(files) > 0
    assert result["test_result"]["exit_code"] == 0
    assert result["git_result"]["status"] == "COMMITTED"

    # Store benchmark record
    bench_dir = Path("var/benchmark")
    bench_dir.mkdir(parents=True, exist_ok=True)
    bench_file = bench_dir / "results.json"

    records = []
    if bench_file.exists():
        try:
            records = json.loads(bench_file.read_text(encoding="utf-8"))
        except Exception:
            records = []

    record = {
        "task_id": task_info["id"],
        "category": task_info["category"],
        "request": task_info["request"],
        "selected_capability": "coding.agent",
        "selected_model": result.get("token_usage", {}).get("model", "qwen2.5-coder:7b"),
        "files_created": files,
        "files_modified": files,
        "tests_run": result.get("test_result", {}).get("status", "PASS"),
        "duration": duration,
        "result": "PASS",
        "failures": 0
    }
    records.append(record)
    bench_file.write_text(json.dumps(records, indent=2), encoding="utf-8")

    await runtime.stop()
