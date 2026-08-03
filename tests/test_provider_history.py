import pytest
from jarvisx.providers.intelligence.provider_history import ProviderHistoryManager

def test_provider_history_learning():
    mgr = ProviderHistoryManager()
    mgr.record_outcome("goose", "Fix bug in auth", success=True, runtime_seconds=1.2, language="Python")
    mgr.record_outcome("goose", "Refactor models", success=True, runtime_seconds=1.5, language="Python")
    mgr.record_outcome("openhands", "Deploy app", success=False, runtime_seconds=4.0)

    assert mgr.get_success_rate("goose") == 1.0
    assert mgr.get_success_rate("openhands") == 0.0
    assert mgr.get_preferred_provider_for_language("python") == "goose"
