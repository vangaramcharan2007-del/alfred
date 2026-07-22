import pytest
import asyncio
from unittest.mock import Mock, patch

from jarvisx.core.skills.capability_context import CapabilityContext
from jarvisx.core.skills.capability_matcher import CapabilityMatcher
from jarvisx.core.skills.skill_ranker import SkillRanker

class MockSkill:
    def __init__(self, name, description, category, tags, success_rate, cost, required_permissions):
        self.name = name
        self.description = description
        self.category = category
        self.tags = tags
        self.success_rate = success_rate
        self.cost = cost
        self.required_permissions = required_permissions

@pytest.fixture
def mock_registry():
    registry = Mock()
    registry.skills = {
        "ResearchSkill": MockSkill("ResearchSkill", "Web search and summary", "research", ["search", "summarize"], 0.9, "low", []),
        "ShadowBrokerOSINT": MockSkill("ShadowBrokerOSINT", "OSINT analysis", "intelligence", ["osint", "research"], 0.85, "medium", ["network_access"]),
        "CodingSkill": MockSkill("CodingSkill", "Write code", "coding", ["code", "python"], 0.8, "high", ["file_system"])
    }
    return registry

@pytest.fixture
def mock_db():
    db = Mock()
    def get_skill_stats(name):
        return {
            "total_runs": 10,
            "success_rate": 0.8,
            "avg_duration_ms": 1500,
            "last_used": None
        }
    db.get_skill_stats = get_skill_stats
    return db

@pytest.fixture
def capability_context(mock_registry, mock_db):
    return CapabilityContext(mock_registry, mock_db)

@pytest.mark.asyncio
async def test_capability_matcher(capability_context):
    matcher = CapabilityMatcher(capability_context)
    
    # Mock LLM router to just return empty so it relies on hybrid rules
    with patch('jarvisx.core.skills.capability_matcher.OmniRouterClient') as mock_router:
        mock_router.return_value.execute = Mock(return_value=asyncio.Future())
        mock_router.return_value.execute.return_value.set_result("")
        
        candidates = await matcher.match("I need OSINT research on a target", "intelligence")
        assert len(candidates) > 0
        
        # ShadowBrokerOSINT should match via tags
        sb_candidate = next((c for c in candidates if c["metadata"]["name"] == "ShadowBrokerOSINT"), None)
        assert sb_candidate is not None
        assert sb_candidate["relevance_score"] >= 0.7

def test_skill_ranker():
    ranker = SkillRanker()
    
    candidates = [
        {
            "metadata": {
                "name": "ShadowBrokerOSINT",
                "cost": "medium",
                "historical_success_rate": 0.9,
                "required_permissions": ["network_access"]
            },
            "relevance_score": 0.8
        },
        {
            "metadata": {
                "name": "ResearchSkill",
                "cost": "low",
                "historical_success_rate": 0.95,
                "required_permissions": []
            },
            "relevance_score": 0.5
        }
    ]
    
    # Rank without permissions: ResearchSkill should win because it needs no permissions and ShadowBroker gets penalized
    ranked = ranker.rank(candidates, available_permissions=[])
    assert ranked[0]["metadata"]["name"] == "ResearchSkill"
    
    # Rank with permissions: ShadowBroker should win because its relevance is higher
    ranked_with_perms = ranker.rank(candidates, available_permissions=["network_access"])
    assert ranked_with_perms[0]["metadata"]["name"] == "ShadowBrokerOSINT"
