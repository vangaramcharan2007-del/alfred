"""
Unit tests for the Jarvis X Autonomic Reflex Sentinel.
"""

import pytest
from jarvisx.reliability.autonomic_sentinel import AutonomicReflexSentinel, HardwareTelemetry
from jarvisx.organism import AlfredOrganism


def test_sentinel_singleton():
    s1 = AutonomicReflexSentinel.get_instance()
    s2 = AutonomicReflexSentinel.get_instance()
    assert s1 is s2


def test_evaluate_cycle_telemetry():
    sentinel = AutonomicReflexSentinel.get_instance()
    telemetry = sentinel.evaluate_cycle()
    assert isinstance(telemetry, HardwareTelemetry)
    assert telemetry.total_ram_gb > 0
    assert telemetry.ram_percent >= 0
    assert telemetry.active_processes_count > 0


def test_trim_memory_working_sets():
    sentinel = AutonomicReflexSentinel.get_instance()
    freed = sentinel.trim_memory_working_sets()
    assert freed >= 0.0
    assert len(sentinel.reflex_events_log) > 0


def test_fastpath_youtube_intent():
    sentinel = AutonomicReflexSentinel.get_instance()
    
    # 1. "open u tube and play telugu songs"
    action = sentinel.resolve_fastpath_intent("open u tube and play telugu songs")
    assert action is not None
    assert action["tool"] == "browser_open"
    assert "youtube.com/results?search_query=telugu%20songs" in action["args"]["url"]
    assert action["fastpath"] is True

    # 2. "play despacito on youtube"
    action2 = sentinel.resolve_fastpath_intent("play despacito on youtube")
    assert action2 is not None
    assert "despacito" in action2["args"]["url"]


def test_fastpath_spotify_intent():
    sentinel = AutonomicReflexSentinel.get_instance()
    action = sentinel.resolve_fastpath_intent("play arijit singh on spotify")
    assert action is not None
    assert action["tool"] == "browser_open"
    assert "spotify.com/search/arijit%20singh" in action["args"]["url"]


def test_fastpath_google_search_intent():
    sentinel = AutonomicReflexSentinel.get_instance()
    action = sentinel.resolve_fastpath_intent("search for quantum computing advancements")
    assert action is not None
    assert action["tool"] == "browser_open"
    assert "google.com/search?q=quantum%20computing%20advancements" in action["args"]["url"]


def test_organism_fastpath_integration():
    import asyncio
    organism = AlfredOrganism(persona="ALFRED")
    assert organism.sentinel is not None
    assert organism.sentinel.is_running is True

    # Run fast-path turn
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(organism.react_turn("open youtube and play lo-fi hip hop"))
    assert res["status"] == "success"
    assert res["fastpath"] is True
    assert res["tool_used"] == "browser_open"
    assert "youtube.com" in res["tool_result"]["result"]["url"]
