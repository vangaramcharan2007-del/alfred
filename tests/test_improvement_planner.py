from jarvisx.meta.performance_monitor import PerformanceMonitor
from jarvisx.meta.performance_analyzer import PerformanceAnalyzer
from jarvisx.meta.failure_memory import FailureMemory
from jarvisx.meta.failure_analyzer import FailureAnalyzer
from jarvisx.meta.improvement_planner import ImprovementPlanner

def test_improvement_planner_generation():
    perf_mon = PerformanceMonitor()
    perf_mon.record_capability_run("java.debugger", success=False, duration_seconds=4.0)

    fail_mem = FailureMemory()
    fail_mem.record_failure("Java debug", "local_agent", "Missing AST parser", "Retry")

    perf_analyzer = PerformanceAnalyzer(monitor=perf_mon)
    fail_analyzer = FailureAnalyzer(failure_memory=fail_mem)

    planner = ImprovementPlanner(performance_analyzer=perf_analyzer, failure_analyzer=fail_analyzer)
    missions = planner.generate_improvement_plan()

    assert len(missions) >= 1
    assert missions[0].priority in [1, 2, 3]
