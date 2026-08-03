import pytest
from jarvisx.diagnostics.capability_checker import CapabilityChecker
from jarvisx.diagnostics.system_health_report import SystemHealthReporter

def test_real_startup_diagnostics():
    checker = CapabilityChecker()
    caps = checker.get_system_capabilities()

    assert "integrations" in caps
    assert caps["integrations"]["Memory"] == "ONLINE"
    assert caps["integrations"]["Agents"] == "ONLINE"

    reporter = SystemHealthReporter(checker=checker)
    banner = reporter.generate_startup_banner()
    assert "JARVIS X" in banner
    assert "Alfred online." in banner
