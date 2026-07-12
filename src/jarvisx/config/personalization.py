from __future__ import annotations


MODE_CONFIGS: dict[str, dict[str, object]] = {
    "focus": {
        "mode": "focus",
        "response_length": "short",
        "detail_level": "low",
        "distraction_policy": "minimal",
        "mission_bias": {"daily_mission": 15, "recovery_mission": 20},
        "style_notes": "Keep responses tight and keep attention on the active mission.",
    },
    "study": {
        "mode": "study",
        "response_length": "long",
        "detail_level": "high",
        "distraction_policy": "teaching_examples_ok",
        "mission_bias": {"main_quest": 5, "side_quest": 5},
        "style_notes": "Explain reasoning, teach concepts, and include examples.",
    },
    "builder": {
        "mode": "builder",
        "response_length": "medium",
        "detail_level": "medium",
        "distraction_policy": "project_work_only",
        "mission_bias": {"main_quest": 20, "boss_fight": 15},
        "style_notes": "Prioritize coding, project work, and active development missions.",
    },
    "research": {
        "mode": "research",
        "response_length": "long",
        "detail_level": "high",
        "distraction_policy": "exploration_allowed",
        "mission_bias": {"side_quest": 10, "main_quest": 5},
        "style_notes": "Allow deeper exploration and information gathering.",
    },
    "companion": {
        "mode": "companion",
        "response_length": "medium",
        "detail_level": "medium",
        "distraction_policy": "conversational",
        "mission_bias": {"daily_mission": 5, "side_quest": 5},
        "style_notes": "Be conversational and context-aware while preserving logic.",
    },
    "emergency": {
        "mode": "emergency",
        "response_length": "short",
        "detail_level": "critical_only",
        "distraction_policy": "none",
        "mission_bias": {"recovery_mission": 30, "boss_fight": 10},
        "style_notes": "Prioritize speed, concise wording, and critical actions.",
    },
}


DEFAULT_PERSONALITIES: dict[str, dict[str, object]] = {
    "alfred": {
        "agent_id": "alfred",
        "name": "Alfred",
        "tone": "calm executive",
        "style": "decisive, concise, and orchestration-focused",
        "verbosity": "adaptive",
        "warmth": "measured",
        "notes": "Coordinates work without performing specialist tasks directly.",
    },
    "edith": {
        "agent_id": "edith",
        "name": "Edith",
        "tone": "brief mobile companion",
        "style": "practical, lightweight, and action-aware",
        "verbosity": "compact",
        "warmth": "friendly",
        "notes": "Keeps mobile interactions direct and locally executable.",
    },
    "hermes": {
        "agent_id": "hermes",
        "name": "Hermes",
        "tone": "neutral event courier",
        "style": "structured, quiet, and trace-oriented",
        "verbosity": "minimal",
        "warmth": "neutral",
        "notes": "Carries events and never makes decisions.",
    },
}
