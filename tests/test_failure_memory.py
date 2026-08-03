from jarvisx.meta.failure_memory import FailureMemory
from jarvisx.meta.failure_analyzer import FailureAnalyzer

def test_failure_memory_and_analyzer():
    mem = FailureMemory()
    mem.record_failure(
        task_description="Build Docker container for Java service",
        provider_id="openhands",
        root_cause="Missing Maven daemon dependency",
        attempted_solution="Re-run container script",
        successful_fix="Switch to Goose provider"
    )

    matches = mem.find_similar_failures("docker")
    assert len(matches) == 1
    assert matches[0].provider_id == "openhands"

    analyzer = FailureAnalyzer(failure_memory=mem)
    fix = analyzer.get_proven_fix("docker")
    assert fix == "Switch to Goose provider"
