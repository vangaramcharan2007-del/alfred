"""Tests for preference auto-discovery.

The property that matters most: a bad config file must never stop the agent
starting. Losing a preference is acceptable; losing the assistant is not, and
for a user who relies on this to function that distinction is the whole point.
"""

from __future__ import annotations

import json

import pytest

from jarvisx.agentic import config as config_module


@pytest.fixture()
def isolated_cwd(tmp_path, monkeypatch):
    """Run inside an empty directory so discovery cannot find repo files."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    return tmp_path


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #


def test_no_config_anywhere_is_not_an_error(isolated_cwd):
    result = config_module.load()
    assert result.found is False
    assert result.values == {}
    assert result.warnings == []


def test_a_project_local_file_is_found(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text(json.dumps({"persona": "jarvis"}))
    result = config_module.load()
    assert result.found is True
    assert result.get("persona") == "jarvis"


def test_an_explicit_path_beats_discovery(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text(json.dumps({"persona": "stark"}))
    other = isolated_cwd / "other.json"
    other.write_text(json.dumps({"persona": "friday"}))
    assert config_module.load(str(other)).get("persona") == "friday"


def test_project_local_beats_the_var_directory(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text(json.dumps({"persona": "jarvis"}))
    scratch = isolated_cwd / "var/agentic"
    scratch.mkdir(parents=True)
    (scratch / "config.json").write_text(json.dumps({"persona": "eevee"}))
    assert config_module.load().get("persona") == "jarvis"


def test_the_var_directory_beats_the_home_directory(isolated_cwd):
    scratch = isolated_cwd / "var/agentic"
    scratch.mkdir(parents=True)
    (scratch / "config.json").write_text(json.dumps({"persona": "eevee"}))
    (isolated_cwd / "home" / ".alfred.json").write_text(json.dumps({"persona": "stark"}))
    assert config_module.load().get("persona") == "eevee"


def test_the_home_directory_is_used_when_nothing_closer_exists(isolated_cwd):
    (isolated_cwd / "home" / ".alfred.json").write_text(json.dumps({"persona": "stark"}))
    assert config_module.load().get("persona") == "stark"


def test_describe_says_where_preferences_came_from(isolated_cwd):
    """No magic: a user wondering why a persona is not applying can find out."""
    assert "no config file" in config_module.load().describe()
    (isolated_cwd / "alfred.json").write_text(json.dumps({"persona": "jarvis"}))
    assert "jarvis" in config_module.load().describe()


# --------------------------------------------------------------------------- #
# Never fatal
# --------------------------------------------------------------------------- #


def test_malformed_json_does_not_stop_the_agent(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text("{ this is not json")
    result = config_module.load()
    assert result.found is False
    assert result.values == {}
    assert result.warnings, "a malformed file must be reported, not swallowed"


def test_a_json_array_is_rejected_rather_than_misread(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text(json.dumps(["persona", "jarvis"]))
    result = config_module.load()
    assert result.found is False
    assert any("expected a JSON object" in w for w in result.warnings)


def test_an_unreadable_file_is_reported(isolated_cwd, monkeypatch):
    broken = isolated_cwd / "alfred.json"
    broken.write_text(json.dumps({"persona": "jarvis"}))
    broken.chmod(0o000)
    try:
        result = config_module.load()
    finally:
        broken.chmod(0o644)
    # Either it reads (running as root) or it warns; it must never raise.
    assert result.found is True or result.warnings


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #


def test_an_unknown_key_is_ignored_not_fatal(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text(
        json.dumps({"persona": "eevee", "typo_key": 12})
    )
    result = config_module.load()
    assert result.get("persona") == "eevee"
    assert any("typo_key" in w for w in result.warnings)


def test_an_invalid_persona_is_rejected_with_a_clear_message(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text(
        json.dumps({"persona": "ultron", "energy": "low"})
    )
    result = config_module.load()
    # The bad key is dropped but the good one survives.
    assert result.get("persona") is None
    assert result.get("energy") == "low"
    assert any("ultron" in w for w in result.warnings)


def test_an_invalid_energy_is_rejected(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text(json.dumps({"energy": "massive"}))
    assert config_module.load().get("energy") is None


def test_every_known_key_round_trips(isolated_cwd):
    values = {
        "persona": "jarvis", "energy": "high", "physical": True,
        "watch": False, "interval": 30, "grace": 10, "state": "x.json",
    }
    (isolated_cwd / "alfred.json").write_text(json.dumps(values))
    result = config_module.load()
    assert result.values == values


# --------------------------------------------------------------------------- #
# Precedence
# --------------------------------------------------------------------------- #


def test_a_cli_flag_beats_the_config_file(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text(
        json.dumps({"persona": "jarvis", "energy": "low"})
    )
    merged = config_module.merge(
        config_module.load(), {"persona": "stark", "energy": None}
    )
    assert merged["persona"] == "stark"
    # A flag nobody passed must not erase the file's value.
    assert merged["energy"] == "low"


def test_merge_does_not_mutate_the_loaded_config(isolated_cwd):
    (isolated_cwd / "alfred.json").write_text(json.dumps({"persona": "jarvis"}))
    loaded = config_module.load()
    config_module.merge(loaded, {"persona": "stark"})
    assert loaded.get("persona") == "jarvis"


# --------------------------------------------------------------------------- #
# Saving
# --------------------------------------------------------------------------- #


def test_save_then_load_round_trips(isolated_cwd):
    target = config_module.save({"persona": "friday", "energy": "high"})
    assert target.exists()
    assert config_module.load(str(target)).get("persona") == "friday"


def test_save_drops_unknown_keys(isolated_cwd):
    target = config_module.save({"persona": "friday", "nonsense": True})
    written = json.loads(target.read_text())
    assert written == {"persona": "friday"}


def test_save_creates_missing_parent_directories(isolated_cwd):
    target = config_module.save({"persona": "eevee"}, isolated_cwd / "a/b/c.json")
    assert target.exists()


def test_save_omits_none_values(isolated_cwd):
    target = config_module.save({"persona": "jarvis", "energy": None})
    assert json.loads(target.read_text()) == {"persona": "jarvis"}


# --------------------------------------------------------------------------- #
# The CLI end to end
# --------------------------------------------------------------------------- #


def test_save_config_remembers_flags_for_next_time(isolated_cwd, capsys):
    from jarvisx.agentic import cli

    cfg = isolated_cwd / "prefs.json"
    assert cli.main([
        "alfred", "--persona", "jarvis", "--energy", "low", "--physical",
        "--save-config", "--config", str(cfg),
    ]) == 0

    written = json.loads(cfg.read_text())
    assert written["persona"] == "jarvis"
    assert written["energy"] == "low"
    assert written["physical"] is True


def test_save_config_does_not_freeze_store_true_defaults(isolated_cwd):
    """Writing quiet=false would pin the default and silently block future change."""
    from jarvisx.agentic import cli

    cfg = isolated_cwd / "prefs.json"
    cli.main(["alfred", "--persona", "eevee", "--save-config", "--config", str(cfg)])
    written = json.loads(cfg.read_text())
    assert "quiet" not in written
    assert "physical_dry_run" not in written


def test_save_config_with_nothing_to_save_explains_itself(isolated_cwd, capsys):
    from jarvisx.agentic import cli

    assert cli.main(["alfred", "--save-config", "--config", str(isolated_cwd / "p.json")]) == 2
    assert "nothing to save" in capsys.readouterr().out


def test_a_saved_config_is_applied_on_the_next_bare_run(isolated_cwd, monkeypatch, capsys):
    """The whole point: no flags on the second launch."""
    from jarvisx.agentic import cli

    cfg = isolated_cwd / "prefs.json"
    cfg.write_text(json.dumps({"persona": "jarvis", "watch": False}))

    monkeypatch.setattr("builtins.input", _fake_input(["quit"]))
    assert cli.main([
        "alfred", "--text", "--no-agent", "--config", str(cfg),
        "--state", str(isolated_cwd / "intake.json"),
    ]) == 0
    out = capsys.readouterr().out
    assert "jarvis -> text" in out


def test_a_cli_flag_overrides_the_saved_config(isolated_cwd, monkeypatch, capsys):
    from jarvisx.agentic import cli

    cfg = isolated_cwd / "prefs.json"
    cfg.write_text(json.dumps({"persona": "jarvis"}))

    monkeypatch.setattr("builtins.input", _fake_input(["quit"]))
    cli.main([
        "alfred", "--text", "--no-agent", "--persona", "stark", "--no-watch",
        "--config", str(cfg), "--state", str(isolated_cwd / "intake.json"),
    ])
    assert "stark -> text" in capsys.readouterr().out


def test_a_broken_config_file_still_starts_the_agent(isolated_cwd, monkeypatch, capsys):
    """The most important case: a typo must not cost you the assistant."""
    from jarvisx.agentic import cli

    cfg = isolated_cwd / "prefs.json"
    cfg.write_text("{ oops")

    monkeypatch.setattr("builtins.input", _fake_input(["quit"]))
    assert cli.main([
        "alfred", "--text", "--no-agent", "--config", str(cfg),
        "--state", str(isolated_cwd / "intake.json"),
    ]) == 0
    out = capsys.readouterr().out
    assert "config:" in out, "the problem should be surfaced, not hidden"


def _fake_input(lines):
    iterator = iter(lines)

    def fake(prompt=""):
        try:
            return next(iterator)
        except StopIteration:
            raise EOFError from None

    return fake
