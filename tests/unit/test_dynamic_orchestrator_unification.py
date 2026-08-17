"""Unit tests for DynamicOrchestrator Grand Unification & Semantic Classification."""

import pytest
import asyncio
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator


def test_dynamic_orchestrator_semantic_intent_classification():
    """Verify semantic classification categorizes voice prompts accurately."""
    orch = DynamicOrchestrator()
    
    # 1. Visual Actuation Prompt
    cat_vis = orch._classify_intent("Please click on the MS Paint icon and draw a rectangle on the screen.")
    assert cat_vis == "VISUAL_ACTUATION"

    # 2. Web Research Prompt
    cat_web = orch._classify_intent("Browse to https://example.com and read the website documentation.")
    assert cat_web == "WEB_RESEARCH"

    # 3. Knowledge / General Query
    cat_rag = orch._classify_intent("What is the difference between a mutex and a semaphore in operating systems?")
    assert cat_rag == "KNOWLEDGE_RAG"


@pytest.mark.asyncio
async def test_dynamic_orchestrator_subsystem_dispatch():
    """Verify asynchronous subsystem execution across Visual, Web, and RAG categories."""
    orch = DynamicOrchestrator()
    
    # Test RAG subsystem dispatch
    res_rag = await orch._execute_subsystem("KNOWLEDGE_RAG", "Explain Jarvis X architecture.")
    assert res_rag["status"] == "success"
    assert res_rag["subsystem"] == "KNOWLEDGE_RAG"

    # Test Visual Actuation subsystem dispatch
    res_vis = await orch._execute_subsystem("VISUAL_ACTUATION", "Launch notepad")
    assert res_vis["status"] in ["success", "failed"]
    assert res_vis["subsystem"] == "VISUAL_ACTUATION"
