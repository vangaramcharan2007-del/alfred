"""Unit & Integration Tests for Long-Term Memory Integration with DynamicOrchestrator.

Covers:
1. Relevant memory retrieved
2. Irrelevant memory excluded on generic queries
3. Bounded context size
4. Memory injection in LLM prompt
5. Cross-session persistence & recall
6. Meaningful facts persisted
7. Trivial noise filtered
8. Secret/credential blocking
9. Tool results separation
10. Memory failure isolation
11. Explicit current user instruction priority
"""

import os
import sys
from pathlib import Path
import pytest

from jarvisx.memory_intelligence.memory_engine import MemoryIntelligenceEngine
from jarvisx.memory_intelligence.models import MemoryType, MemorySource
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator


class FakeMemoryRouter:
    """Mock LLMRouter that records prompts and returns pre-configured responses."""
    def __init__(self, responses: list | dict):
        self.responses = responses
        self.call_history = []
        self._index = 0

    def route_request_sync(self, prompt: str, require_offline: bool = False, model_override: str = None):
        self.call_history.append(prompt)
        if isinstance(self.responses, list):
            if self._index < len(self.responses):
                resp = self.responses[self._index]
                self._index += 1
            else:
                resp = "Default fake response"
            return {
                "status": "success",
                "provider_id": "fake.local",
                "result": {"status": "AVAILABLE", "response": resp}
            }
        elif isinstance(self.responses, dict):
            for key, resp in self.responses.items():
                if key in prompt:
                    return {
                        "status": "success",
                        "provider_id": "fake.local",
                        "result": {"status": "AVAILABLE", "response": resp}
                    }
            return {
                "status": "success",
                "provider_id": "fake.local",
                "result": {"status": "AVAILABLE", "response": "Default fake response"}
            }


@pytest.fixture
def temp_memory_db(tmp_path):
    db_file = str(tmp_path / "test_memory.db")
    return db_file


def test_relevant_memory_retrieved(temp_memory_db):
    """Relevant memory is retrieved and injected for personal/preference queries."""
    engine = MemoryIntelligenceEngine(db_path=temp_memory_db)
    engine.remember("I prefer local-first AI architecture", memory_type=MemoryType.SEMANTIC)

    fake_router = FakeMemoryRouter(["You prefer local-first AI, Sir."])
    orch = DynamicOrchestrator(llm_router=fake_router, memory_engine=engine)

    res = orch.execute_llm_request("What kind of AI architecture do I prefer?", persona="ALFRED")
    assert res["action"] == "llm"
    assert len(fake_router.call_history) == 1
    prompt = fake_router.call_history[0]
    assert "[PERSONAL MEMORY & USER CONTEXT]" in prompt
    assert "local-first AI architecture" in prompt


def test_irrelevant_memory_excluded(temp_memory_db):
    """Generic/unrelated queries do not dump personal project memories."""
    engine = MemoryIntelligenceEngine(db_path=temp_memory_db)
    engine.remember("Targeting 10 CGPA in BTech", memory_type=MemoryType.SEMANTIC)
    engine.remember("Prefer dark mode in VS Code", memory_type=MemoryType.SEMANTIC)

    fake_router = FakeMemoryRouter(["A CPU is the central processing unit."])
    orch = DynamicOrchestrator(llm_router=fake_router, memory_engine=engine)

    res = orch.execute_llm_request("What is a CPU?", persona="ALFRED")
    assert res["action"] == "llm"
    prompt = fake_router.call_history[0]
    # Unrelated general query must not contain personal memory dump
    assert "10 CGPA" not in prompt
    assert "dark mode" not in prompt


def test_bounded_context_size(temp_memory_db):
    """Context retrieval stays bounded even with many stored records."""
    engine = MemoryIntelligenceEngine(db_path=temp_memory_db)
    for i in range(25):
        engine.remember(f"Project milestone {i} completed", memory_type=MemoryType.EPISODIC)

    ctx = engine.get_personal_context(query="What are my project milestones?")
    assert len(ctx.episodic_highlights) <= 6
    assert len(ctx.prompt_block.splitlines()) <= 10


def test_cross_session_persistence(temp_memory_db):
    """Memories persisted in session 1 are recalled in a fresh session 2."""
    # Session 1: Store memory
    engine1 = MemoryIntelligenceEngine(db_path=temp_memory_db)
    ok, mem, _ = engine1.remember("My current project goal is tool execution for Jarvis X", memory_type=MemoryType.SEMANTIC)
    assert ok and mem

    # Session 2: Fresh engine instance pointing to the same DB
    engine2 = MemoryIntelligenceEngine(db_path=temp_memory_db)
    fake_router = FakeMemoryRouter(["Your focus is tool execution for Jarvis X, Sir."])
    orch = DynamicOrchestrator(llm_router=fake_router, memory_engine=engine2)

    res = orch.execute_llm_request("What should I work on next for Jarvis?", persona="ALFRED")
    assert res["action"] == "llm"
    prompt = fake_router.call_history[0]
    assert "tool execution for Jarvis X" in prompt


def test_meaningful_facts_persisted_automatically(temp_memory_db):
    """Meaningful facts in user conversation are stored automatically after the turn."""
    engine = MemoryIntelligenceEngine(db_path=temp_memory_db)
    fake_router = FakeMemoryRouter(["Understood, Sir."])
    orch = DynamicOrchestrator(llm_router=fake_router, memory_engine=engine)

    orch.execute_llm_request("I prefer offline AI inference.", persona="ALFRED")
    counts = engine.store.count_memories()
    assert counts["total_active"] >= 1

    memories = engine.recall(limit=10)
    assert any("offline AI inference" in m.content for m in memories)


def test_trivial_noise_not_persisted(temp_memory_db):
    """Greetings, acknowledgments, and trivial math are not stored in memory."""
    engine = MemoryIntelligenceEngine(db_path=temp_memory_db)
    fake_router = FakeMemoryRouter(["Hello Sir!", "You are welcome.", "4"])
    orch = DynamicOrchestrator(llm_router=fake_router, memory_engine=engine)

    orch.execute_llm_request("hello", persona="ALFRED")
    orch.execute_llm_request("thank you", persona="ALFRED")
    orch.execute_llm_request("what is 2 + 2", persona="ALFRED")

    counts = engine.store.count_memories()
    assert counts["total_active"] == 0


def test_secrets_are_blocked_from_memory(temp_memory_db):
    """Credentials, passwords, and API keys are blocked from being stored."""
    engine = MemoryIntelligenceEngine(db_path=temp_memory_db)
    fake_router = FakeMemoryRouter(["I will keep that safe, Sir."])
    orch = DynamicOrchestrator(llm_router=fake_router, memory_engine=engine)

    orch.execute_llm_request("Remember my secret key = ghp_111122223333444455556666777788889999", persona="ALFRED")
    counts = engine.store.count_memories()
    assert counts["total_active"] == 0


def test_tool_results_not_dumped_into_long_term_memory(temp_memory_db):
    """Tool results (e.g. system info, file contents) remain separate and are not written to long-term memory."""
    engine = MemoryIntelligenceEngine(db_path=temp_memory_db)
    fake_router = FakeMemoryRouter([
        '{"type": "tool_call", "tool": "get_system_info", "arguments": {}}',
        "You have 16 GB of RAM, Sir."
    ])
    orch = DynamicOrchestrator(llm_router=fake_router, memory_engine=engine)

    res = orch.execute_llm_request("How much RAM do I have?", persona="ALFRED")
    assert res["action"] == "tool_call"
    # The tool result is present in execution_steps
    assert len(res["execution_steps"]) == 1

    # But long-term memory count is 0 because "How much RAM do I have?" is a query, not a preference/fact to remember
    counts = engine.store.count_memories()
    assert counts["total_active"] == 0


def test_memory_failure_isolation():
    """If the memory engine throws an exception, LLM execution proceeds without crashing."""
    class BrokenMemoryEngine:
        def get_personal_context(self, query=""):
            raise RuntimeError("Database corrupted or unavailable")

        def extract_and_store_from_conversation(self, text=""):
            raise RuntimeError("Disk full")

    fake_router = FakeMemoryRouter(["I am operating normally, Sir."])
    orch = DynamicOrchestrator(llm_router=fake_router, memory_engine=BrokenMemoryEngine())

    # Must complete normally despite broken memory engine
    res = orch.execute_llm_request("Explain quantum computing in one sentence.", persona="ALFRED")
    assert res["action"] == "llm"
    assert "operating normally" in res["response"]


def test_explicit_instruction_priority(temp_memory_db):
    """The injected memory prompt explicitly marks memory as background context overridden by current instruction."""
    engine = MemoryIntelligenceEngine(db_path=temp_memory_db)
    engine.remember("I prefer Python for all automation tasks", memory_type=MemoryType.SEMANTIC)

    fake_router = FakeMemoryRouter(["Writing script in Rust as requested, Sir."])
    orch = DynamicOrchestrator(llm_router=fake_router, memory_engine=engine)

    res = orch.execute_llm_request("Write a script in Rust instead of Python", persona="ALFRED")
    assert res["action"] == "llm"
    prompt = fake_router.call_history[0]
    assert "prioritize" in prompt.lower()
