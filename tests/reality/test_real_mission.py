import pytest
from jarvisx.benchmark.runner import BenchmarkRunner

def test_real_benchmark_execution():
    runner = BenchmarkRunner(var_dir="var/test_reality")
    results = runner.run_all()
    assert len(results) == 5
    assert all(r.success for r in results)
