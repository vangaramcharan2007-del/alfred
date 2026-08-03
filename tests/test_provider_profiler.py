import pytest
from jarvisx.providers.intelligence.provider_profiler import ProviderProfiler, ProviderProfile

def test_provider_profiler_simulations():
    profiler = ProviderProfiler()
    profiles = profiler.list_profiles()

    assert len(profiles) >= 5
    goose = profiler.get_profile("goose")
    assert goose is not None
    assert goose.provider_name == "Goose Autonomous Engineer"
    assert "python" in goose.supported_languages

    openhands = profiler.get_profile("openhands")
    assert openhands is not None
    assert openhands.permission_level == "EXECUTE"
