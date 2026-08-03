from jarvisx.meta.performance_monitor import PerformanceMonitor
from jarvisx.meta.performance_analyzer import PerformanceAnalyzer

def test_performance_monitor_and_analyzer():
    monitor = PerformanceMonitor()
    monitor.record_capability_run("goose.engineering", success=True, duration_seconds=1.2)
    monitor.record_capability_run("openhands.engineering", success=False, duration_seconds=3.0)
    monitor.record_capability_run("openhands.engineering", success=False, duration_seconds=3.5)

    summary = monitor.get_performance_summary()
    assert summary["goose.engineering"]["success_rate"] == 1.0
    assert summary["openhands.engineering"]["success_rate"] == 0.0

    analyzer = PerformanceAnalyzer(monitor=monitor)
    degraded = analyzer.detect_degraded_capabilities(threshold=0.80)

    assert len(degraded) == 1
    assert degraded[0]["capability_id"] == "openhands.engineering"
