"""Regression tests for the `friday` console script.

`friday = "friday.__main__:main"` is declared in pyproject.toml. It used to
ignore argv entirely, so --help launched the dashboard, and its one behaviour
was reached through a method named `run_interactive_shell` -- a name that
promised an input loop that does not exist anywhere in the package.
"""

import sys

import friday.__main__ as entry


def test_help_prints_usage_and_exits_zero(capsys):
    sys.argv = ["friday", "--help"]
    assert entry.main() == 0

    out = capsys.readouterr().out
    assert "executive dashboard" in out
    # Must state plainly that there is no REPL, or the name/history invites the
    # wrong expectation again.
    assert "no interactive mode" in out.lower()


def test_short_help_behaves_the_same(capsys):
    sys.argv = ["friday", "-h"]
    assert entry.main() == 0
    assert "executive dashboard" in capsys.readouterr().out


def test_unknown_flag_is_rejected_not_silently_ignored(capsys):
    """A typo'd flag that appears to succeed is worse than one that reports."""
    sys.argv = ["friday", "--bogus"]
    code = entry.main()

    assert code == 2
    err = capsys.readouterr().err
    assert "--bogus" in err


def test_no_args_shows_the_dashboard(monkeypatch, capsys):
    called = {}

    class FakeAssistant:
        def show_dashboard(self):
            called["yes"] = True

    monkeypatch.setattr(entry, "FridayAssistant", FakeAssistant)

    sys.argv = ["friday"]
    assert entry.main() == 0
    assert called.get("yes") is True


def test_renamed_method_exists_and_old_name_is_gone():
    """The rename is the point: a method named `run_interactive_shell` whose body
    printed a dashboard and returned was a claim the code did not back -- there
    is no input loop anywhere in this package."""
    import importlib

    cls = importlib.import_module("friday.friday_assistant").FridayAssistant

    assert hasattr(cls, "show_dashboard"), "renamed method missing"
    assert not hasattr(cls, "run_interactive_shell"), (
        "the misleading name is still present"
    )
