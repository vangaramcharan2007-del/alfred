"""
Unit Tests for Autonomous Agent Trainer & Fine-Tuning Engine.
"""

import pytest
from jarvisx.agents.agent_trainer_engine import AgentTrainerEngine, get_agent_trainer


def test_agent_trainer_singleton():
    trainer1 = get_agent_trainer()
    trainer2 = get_agent_trainer()
    assert trainer1 is trainer2


def test_agent_trainer_fleet_training():
    trainer = get_agent_trainer()
    res = trainer.train_and_update_fleet()
    assert res.get("status") == "success"
    assert res.get("agents_trained_count") >= 4
    
    # Check default profiles exist
    assert "dsa_tutor" in trainer.agent_profiles
    assert "coder_agent" in trainer.agent_profiles
    assert "researcher_agent" in trainer.agent_profiles
    assert "security_agent" in trainer.agent_profiles

    # Check skills were equipped
    dsa_profile = trainer.agent_profiles["dsa_tutor"]
    assert len(dsa_profile.system_prompt) > 20
    assert len(dsa_profile.few_shot_examples) >= 1


def test_agent_trainer_benchmark_fleet():
    trainer = get_agent_trainer()
    bench = trainer.benchmark_fleet()
    assert bench.get("status") == "success"
    assert "fleet_average_score" in bench
    assert len(bench.get("benchmark_results", {})) >= 4
