"""Regression tests for the `jarvis` console script (jarvisx.cli).

`jarvis = "jarvisx.cli:main"` is declared in pyproject.toml, so this is a
primary entry point. It used to crash on every invocation -- including --help --
before any command could run.
"""

import sys

import pytest

import jarvisx.cli as cli


def test_help_does_not_crash(capsys):
    """The parser used to raise AttributeError while being built.

    `add_parser` belongs to the subparsers action, not to the parser that
    add_parser() returns, so `chat_p.add_parser("prompt", ...` blew up during
    parser construction -- before argparse ever looked at sys.argv.
    """
    sys.argv = ["jarvis", "--help"]
    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "JARVIS X Autonomous OS" in out
    for cmd in ("boot", "status", "ui", "chat"):
        assert cmd in out, f"{cmd} missing from help"


def test_no_subcommand_prints_help_instead_of_crashing(capsys):
    sys.argv = ["jarvis"]
    cli.main()

    assert "JARVIS X Autonomous OS" in capsys.readouterr().out


def test_chat_joins_a_multi_word_prompt(monkeypatch):
    """`prompt` is nargs="+", so the words arrive as a list and are rejoined.

    Asserted against the parser rather than the network: headless_chat is
    patched out, so this proves the CLI parses and dispatches, which is the part
    that was broken.
    """
    seen = {}
    monkeypatch.setattr(cli, "headless_chat", lambda text: seen.setdefault("text", text))

    sys.argv = ["jarvis", "chat", "what", "time", "is", "it"]
    cli.main()

    assert seen.get("text") == "what time is it"


def test_chat_requires_a_prompt():
    """With nargs="+" an empty prompt is a usage error, not a silent no-op."""
    sys.argv = ["jarvis", "chat"]
    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code != 0
