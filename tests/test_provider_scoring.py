import pytest
from jarvisx.providers.intelligence.provider_profiler import ProviderProfile
from jarvisx.providers.intelligence.provider_scoring import ProviderScorer

def test_provider_scoring_match():
    scorer = ProviderScorer()
    profile = ProviderProfile(
        provider_id="test_prov",
        provider_name="Test Provider",
        supported_languages=["python", "typescript"],
        supported_frameworks=["fastapi"],
        supported_tasks=["Bug Fix", "Refactoring"],
        average_latency=0.2,
        average_cost=0.0,
        average_success_rate=0.98,
        offline_support=True,
        health_status="HEALTHY"
    )

    score = scorer.compute_score(
        profile=profile,
        task_description="Fix critical authentication bug",
        language="Python",
        framework="FastAPI",
        require_offline=True
    )

    assert score >= 0.85

def test_unhealthy_provider_score_zero():
    scorer = ProviderScorer()
    profile = ProviderProfile(
        provider_id="dead_prov",
        provider_name="Dead Provider",
        health_status="UNHEALTHY"
    )

    score = scorer.compute_score(profile=profile, task_description="Fix bug")
    assert score == 0.0
