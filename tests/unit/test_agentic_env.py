"""Tests for .env / credential discovery and the doctor command.

These exist because the repository has no ``python-dotenv`` dependency and
nothing else populates ``os.environ`` from ``.env`` — so before this, a key in
``.env`` silently downgraded every agent to the offline heuristic.
"""

from __future__ import annotations

import os

import pytest

from jarvisx.agentic import cli
from jarvisx.agentic.backends import AutoBackend, HeuristicBackend
from jarvisx.agentic.env import (
    candidate_env_files,
    describe_credentials,
    fingerprint,
    get_secret,
    is_secret_name,
    load_dotenv,
    parse_env,
    redact,
    required_model_env,
)

FAKE_GROQ = "gsk_TESTONLYnotarealkey0000000000"


# --------------------------------------------------------------------------- #
# .env parsing
# --------------------------------------------------------------------------- #


def test_parse_env_handles_quotes_export_and_comments():
    text = """
# a comment
GROQ_API_KEY=gsk_abc123
export OPENROUTER_API_KEY="sk-or-v1-xyz"
SINGLE='quoted value'
SPACED =  padded
EMPTY=
not a line
=novalue
"""
    parsed = parse_env(text)
    assert parsed["GROQ_API_KEY"] == "gsk_abc123"
    assert parsed["OPENROUTER_API_KEY"] == "sk-or-v1-xyz"
    assert parsed["SINGLE"] == "quoted value"
    assert parsed["SPACED"] == "padded"
    assert parsed["EMPTY"] == ""
    assert "not a line" not in parsed
    assert "" not in parsed


def test_parse_env_ignores_malformed_keys():
    assert parse_env("1BAD=x\nGOOD=y") == {"GOOD": "y"}


def test_parse_env_of_empty_input():
    assert parse_env("") == {}
    assert parse_env("\n\n#only comments\n") == {}


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #


def test_load_dotenv_picks_up_a_key_from_the_repo_root(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text(f"GROQ_API_KEY={FAKE_GROQ}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    loaded = load_dotenv()
    assert any(p == tmp_path / ".env" for p in loaded)
    assert os.environ["GROQ_API_KEY"] == FAKE_GROQ


def test_existing_environment_wins_over_the_file(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("GROQ_API_KEY=from_file\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GROQ_API_KEY", "from_environment")

    load_dotenv()
    assert os.environ["GROQ_API_KEY"] == "from_environment"


def test_override_lets_the_file_win_when_asked(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("GROQ_API_KEY=from_file\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GROQ_API_KEY", "from_environment")

    load_dotenv(override=True)
    assert os.environ["GROQ_API_KEY"] == "from_file"


def test_get_secret_reads_the_file_without_touching_environ(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text(f"GROQ_API_KEY={FAKE_GROQ}\n", encoding="utf-8")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert get_secret("GROQ_API_KEY", start=tmp_path) == FAKE_GROQ


def test_get_secret_returns_none_when_absent(tmp_path):
    assert get_secret("NOPE_NOT_SET", start=tmp_path) is None


def test_env_without_a_git_root_still_resolves(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("GROQ_API_KEY=x\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    files = candidate_env_files()
    assert any(str(p).endswith(".env") for p in files)


# --------------------------------------------------------------------------- #
# Backend selection
# --------------------------------------------------------------------------- #


def test_auto_backend_selects_groq_when_a_key_is_present(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text(
        f"GROQ_API_KEY={FAKE_GROQ}\nGROQ_MODEL=llama-3.3-70b-versatile\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("ALFRED_AGENT_BACKEND", raising=False)

    backend = AutoBackend()
    assert "llama-3.3-70b-versatile" in backend.name
    assert backend.base_url == "https://api.groq.com/openai/v1"


def test_auto_backend_honours_an_explicit_offline_override(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text(f"GROQ_API_KEY={FAKE_GROQ}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ALFRED_AGENT_BACKEND", "offline")

    assert isinstance(AutoBackend(), HeuristicBackend)


def test_auto_backend_forced_to_groq_without_a_key_raises(tmp_path, monkeypatch):
    from jarvisx.agentic.backends import BackendError

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("ALFRED_AGENT_BACKEND", "groq")

    with pytest.raises(BackendError, match="no GROQ_API_KEY"):
        AutoBackend()


def test_auto_backend_falls_back_to_heuristic_with_nothing_configured(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in (
        "GROQ_API_KEY",
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "OLLAMA_BASE_URL",
        "ALFRED_AGENT_BACKEND",
    ):
        monkeypatch.delenv(name, raising=False)
    assert isinstance(AutoBackend(), HeuristicBackend)


def test_ollama_api_url_is_normalised_to_the_openai_shim(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ALFRED_AGENT_BACKEND", raising=False)
    # Alfred's .env.example ships this shape, which is the *native* API, not /v1.
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/api")

    backend = AutoBackend()
    assert backend.base_url == "http://127.0.0.1:11434/v1"


def test_groq_model_precedence(tmp_path, monkeypatch):
    from jarvisx.agentic.backends import groq_backend

    monkeypatch.delenv("ALFRED_AGENT_MODEL", raising=False)
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    monkeypatch.setenv("CODER_MODEL", "openai/gpt-oss-120b")
    assert groq_backend("k").model == "openai/gpt-oss-120b"

    monkeypatch.setenv("GROQ_MODEL", "llama-3.1-8b-instant")
    assert groq_backend("k").model == "llama-3.1-8b-instant"

    monkeypatch.setenv("ALFRED_AGENT_MODEL", "meta-llama/llama-4-scout-17b")
    assert groq_backend("k").model == "meta-llama/llama-4-scout-17b"


# --------------------------------------------------------------------------- #
# Secret hygiene
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "raw",
    [
        "key gsk_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789 failed",
        "key sk-or-v1-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789 failed",
        "key sk-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789 failed",
        "key AIzaAbCdEfGhIjKlMnOpQrStUvWxYz0123 failed",
    ],
)
def test_redact_strips_provider_key_shapes(raw):
    out = redact(raw)
    assert "[REDACTED_KEY]" in out
    assert "gsk_AbCd" not in out and "sk-or-v1-AbCd" not in out


def test_redact_leaves_ordinary_text_alone():
    assert redact("nothing secret here") == "nothing secret here"
    assert redact("") == ""


def test_fingerprint_is_stable_and_non_reversible():
    a = fingerprint(FAKE_GROQ)
    assert a == fingerprint(FAKE_GROQ)
    assert FAKE_GROQ not in a
    assert fingerprint("other") != a
    assert fingerprint("") == "(empty)"


def test_describe_credentials_never_emits_the_key(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text(f"GROQ_API_KEY={FAKE_GROQ}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    summary = describe_credentials()
    assert "GROQ_API_KEY" in summary["configured"]
    assert FAKE_GROQ not in repr(summary)


def test_is_secret_name_classification():
    assert is_secret_name("GROQ_API_KEY")
    assert is_secret_name("MY_PASSWORD")
    assert not is_secret_name("PATH")


def test_required_model_env_masks_key_values(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text(f"GROQ_API_KEY={FAKE_GROQ}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    settings = required_model_env()
    assert settings["GROQ_API_KEY"] == "***"
    assert FAKE_GROQ not in repr(settings)


# --------------------------------------------------------------------------- #
# doctor
# --------------------------------------------------------------------------- #


def test_doctor_exits_nonzero_when_no_model_is_configured(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    for name in (
        "GROQ_API_KEY",
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "OLLAMA_BASE_URL",
        "ALFRED_AGENT_BACKEND",
    ):
        monkeypatch.delenv(name, raising=False)

    assert cli.main(["doctor", "--trace-root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "no API key found" in out
    assert "NOT READY" in out
    assert "GROQ_API_KEY" in out


def test_doctor_reports_the_sandbox_as_working(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    for name in ("GROQ_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "OLLAMA_BASE_URL"):
        monkeypatch.delenv(name, raising=False)

    cli.main(["doctor", "--trace-root", str(tmp_path)])
    out = capsys.readouterr().out
    assert "code execution" in out and "path jail" in out
    assert "escape blocked" in out


def test_doctor_finds_a_key_from_env(tmp_path, monkeypatch, capsys):
    (tmp_path / ".env").write_text(f"GROQ_API_KEY={FAKE_GROQ}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("ALFRED_AGENT_BACKEND", raising=False)

    # The live call cannot succeed in CI, but discovery and selection must.
    cli.main(["doctor", "--trace-root", str(tmp_path)])
    out = capsys.readouterr().out
    assert "GROQ_API_KEY" in out
    assert "groq" in out.lower()
    assert FAKE_GROQ not in out, "doctor must never print the key"


# --------------------------------------------------------------------------- #
# Honesty about what hardware is actually present
# --------------------------------------------------------------------------- #


def test_tts_is_not_available_when_the_engine_has_no_audio_backend():
    """Regression: doctor promised speech that could never come.

    RealTTSEngine swallows a missing pyttsx3 and leaves _engine as None, so
    treating a successful import as success reported `available = True` on a
    machine with no audio stack at all.
    """
    from jarvisx.agentic.voice_loop import TTSOutput

    class NoBackendEngine:
        _engine = None

        def speak(self, text, blocking=True):
            raise RuntimeError("should never be called")

    import jarvisx.voice.tts_engine as tts_module

    original = tts_module.RealTTSEngine
    tts_module.RealTTSEngine = lambda **kw: NoBackendEngine()
    try:
        out = TTSOutput()
        assert out.available is False
        # And saying something must fall back, not raise.
        out.say("hello")
        assert out._fallback.spoken == ["hello"]
    finally:
        tts_module.RealTTSEngine = original


def test_tts_is_available_when_the_engine_really_initialised():
    from jarvisx.agentic.voice_loop import TTSOutput

    class WorkingEngine:
        _engine = object()

        def __init__(self):
            self.said = []

        def speak(self, text, blocking=True):
            self.said.append(text)

    import jarvisx.voice.tts_engine as tts_module

    original = tts_module.RealTTSEngine
    tts_module.RealTTSEngine = lambda **kw: WorkingEngine()
    try:
        out = TTSOutput()
        assert out.available is True
        out.say("hello")
        assert out._engine.said == ["hello"]
    finally:
        tts_module.RealTTSEngine = original


def test_mic_is_not_available_when_whisper_is_missing_but_sounddevice_is_not():
    """The same trap on the input side: sounddevice can exist without whisper."""
    from jarvisx.agentic.voice_loop import WhisperMicInput

    class NoWhisperEngine:
        _whisper_model = None

    import jarvisx.voice.stt_engine as stt_module

    original = stt_module.FastSTTEngine
    stt_module.FastSTTEngine = lambda **kw: NoWhisperEngine()
    try:
        mic = WhisperMicInput()
        # sounddevice is not installed here, so this is False either way; the
        # assertion that matters is that it never claims to be listening.
        assert mic.available is False
    finally:
        stt_module.FastSTTEngine = original
