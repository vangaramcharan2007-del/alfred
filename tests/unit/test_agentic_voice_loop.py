"""Tests for the voice loop: routing, policy gate, capture and agent hand-off."""

from __future__ import annotations

import pytest

from jarvisx.agentic.intake import Energy, IntakeEngine, ItemKind
from jarvisx.agentic.voice_loop import (
    ConsoleInput,
    ConsoleOutput,
    Intent,
    VoiceAgentLoop,
    route,
    strip_trigger,
)

DUMP = (
    "brain dump: um i need to write the OS assignment its due today, "
    "also reply to that email from the professor, "
    "oh and i'm really worried about failing this semester, "
    "someone should really fix the lab printer"
)


# --------------------------------------------------------------------------- #
# Trigger stripping
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("brain dump: write the report", "write the report"),
        ("brain dump - write the report", "write the report"),
        ("dump, write the report", "write the report"),
        ("here's everything: pay rent, call mum", "pay rent, call mum"),
        ("remember this: book the dentist", "book the dentist"),
        ("note to self: stretch", "stretch"),
        ("write the report", "write the report"),  # untouched
        ("", ""),
    ],
)
def test_strip_trigger(raw, expected):
    assert strip_trigger(raw) == expected


def test_strip_trigger_falls_back_to_the_original_when_only_a_trigger():
    # Nothing to capture, but we must not return "" and lose the utterance.
    assert strip_trigger("brain dump:") == "brain dump:"


# --------------------------------------------------------------------------- #
# Routing
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "text,expected",
    [
        ("help", Intent.HELP),
        ("what can you do", Intent.HELP),
        ("status", Intent.STATUS),
        ("show me my list", Intent.STATUS),
        ("what should I do", Intent.WHAT_NEXT),
        ("what's next", Intent.WHAT_NEXT),
        ("I'm stuck", Intent.WHAT_NEXT),
        ("i don't know where to start", Intent.WHAT_NEXT),
        ("done with the email", Intent.DONE),
        ("finished", Intent.DONE),
        ("brain dump: pay rent", Intent.BRAIN_DUMP),
        ("here's everything on my plate right now", Intent.BRAIN_DUMP),
        ("build a csv deduplicator", Intent.DO_WORK),
        # No artifact named, so this is a task to capture, not code to write.
        ("write the report", Intent.BRAIN_DUMP),
        ("Alfred, fix the login bug", Intent.DO_WORK),
        ("please run the tests", Intent.DO_WORK),
        ("", Intent.UNKNOWN),
    ],
)
def test_route(text, expected):
    assert route(text) is expected


def test_route_treats_a_long_rambling_sentence_as_a_dump():
    long_text = "so there is this thing and also that thing and another thing entirely"
    assert route(long_text) is Intent.BRAIN_DUMP


def test_route_never_treats_a_decision_request_as_work():
    """"What should I do" must not launch an agent."""
    assert route("what should I do about the report") is Intent.WHAT_NEXT


def test_route_requires_an_explicit_verb_to_authorise_execution():
    assert route("the report") is Intent.UNKNOWN
    assert route("assignment") is Intent.UNKNOWN


# --------------------------------------------------------------------------- #
# Console I/O fallbacks
# --------------------------------------------------------------------------- #


def test_console_input_replays_scripted_lines_then_exhausts():
    stt = ConsoleInput(lines=["one", "two"])
    assert stt.listen() == "one"
    assert stt.listen() == "two"
    assert stt.listen() is None


def test_console_output_collects_everything_it_said(capsys):
    tts = ConsoleOutput()
    tts.say("hello")
    tts.say("world")
    assert tts.spoken == ["hello", "world"]
    assert "hello" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# The loop
# --------------------------------------------------------------------------- #


def _loop(lines, **kwargs):
    tts = ConsoleOutput()
    loop = VoiceAgentLoop(
        stt=ConsoleInput(lines=lines), tts=tts, energy=kwargs.pop("energy", Energy.MEDIUM), **kwargs
    )
    return loop, tts


def test_brain_dump_captures_and_suggests_one_thing():
    loop, tts = _loop([DUMP], energy=Energy.LOW)
    turns = loop.run()

    assert turns[0].intent is Intent.BRAIN_DUMP
    assert len(loop.intake.items) == 4
    assert "4 things" in tts.spoken[0]
    # Low energy must not hand over the 45-minute assignment.
    assert "email" in tts.spoken[0].lower()


def test_brain_dump_titles_do_not_contain_the_trigger_phrase():
    loop, _ = _loop([DUMP])
    loop.run()
    for item in loop.intake.items:
        assert "brain dump" not in item.title.lower()
        assert "brain dump" not in item.raw.lower()


def test_brain_dump_separates_out_things_that_are_not_yours():
    loop, tts = _loop([DUMP])
    loop.run()
    kinds = {i.kind for i in loop.intake.items}
    assert ItemKind.WORRY in kinds and ItemKind.DELEGATE in kinds
    assert "not yours" in tts.spoken[0]


def test_what_next_gives_exactly_one_task_and_a_first_step():
    loop, tts = _loop([DUMP, "what should I do"], energy=Energy.LOW)
    turns = loop.run()

    assert turns[1].intent is Intent.WHAT_NEXT
    spoken = tts.spoken[1]
    assert "Do this one" in spoken
    assert "Start by" in spoken
    assert turns[1].payload["steps"]


def test_what_next_with_nothing_captured_asks_for_a_dump():
    loop, tts = _loop(["what should I do"])
    loop.run()
    assert "Nothing captured" in tts.spoken[0]


def test_done_closes_an_item_and_offers_the_next():
    loop, tts = _loop([DUMP, "done with the email"], energy=Energy.LOW)
    turns = loop.run()

    assert turns[1].intent is Intent.DONE
    completed = turns[1].payload["completed"]
    assert "email" in completed["raw"].lower()
    # The item must actually be closed, and gone from the open list.
    assert completed["done"] is True
    assert completed["id"] not in [i.id for i in loop.intake.open_items]
    assert "Done:" in tts.spoken[1]


def test_done_with_an_unknown_item_says_so():
    loop, tts = _loop([DUMP, "done with the spaceship"])
    loop.run()
    assert "could not find" in tts.spoken[1]


def test_status_reports_open_items():
    loop, tts = _loop([DUMP, "status"])
    turns = loop.run()
    assert turns[1].intent is Intent.STATUS
    assert turns[1].payload["open_items"] == 4


def test_status_on_an_empty_list_is_honest():
    loop, tts = _loop(["status"])
    loop.run()
    assert "empty" in tts.spoken[0]


def test_destructive_commands_are_blocked_by_the_policy_gate():
    loop, tts = _loop(["rm -rf /"])
    turns = loop.run()
    assert turns[0].blocked is True
    assert "not running that" in tts.spoken[0]
    assert loop.intake.items == [], "a blocked command must not be captured as a task"


def test_wake_word_alone_is_acknowledged():
    loop, tts = _loop(["hey alfred"])
    turns = loop.run()
    assert turns[0].intent is Intent.HELP
    assert "listening" in tts.spoken[0]


def test_wake_word_is_stripped_before_routing():
    loop, _ = _loop(["alfred, write the report"])
    turns = loop.run()
    assert turns[0].intent is Intent.DO_WORK


def test_do_work_without_a_runner_explains_rather_than_failing():
    loop, tts = _loop(["build a csv deduplicator"])
    turns = loop.run()
    assert turns[0].intent is Intent.DO_WORK
    assert "doctor" in tts.spoken[0]


def test_do_work_hands_the_goal_to_the_injected_runner():
    seen = []

    def runner(goal):
        seen.append(goal)
        return {"ok": True, "succeeded": ["a", "b"]}

    loop, tts = _loop(["build a csv deduplicator"], runner=runner)
    turns = loop.run()
    assert seen == ["build a csv deduplicator"]
    assert "2 steps" in tts.spoken[0]


def test_do_work_reports_a_runner_failure_out_loud():
    def runner(goal):
        raise RuntimeError("model exploded")

    loop, tts = _loop(["build a parser"], runner=runner)
    turns = loop.run()
    assert "model exploded" in tts.spoken[0]


def test_do_work_reports_a_failed_run():
    loop, tts = _loop(
        ["build a parser"], runner=lambda g: {"ok": False, "failed": ["verify"], "error": "tests broke"}
    )
    loop.run()
    assert "tests broke" in tts.spoken[0]


def test_ambiguous_speech_is_captured_not_guessed():
    loop, tts = _loop(["the thing with the printer"])
    turns = loop.run()
    assert turns[0].intent is Intent.UNKNOWN
    assert len(loop.intake.items) == 1
    assert "wrote that down" in tts.spoken[0]


def test_empty_transcript_is_handled_gracefully():
    loop, tts = _loop(["", "   "])
    turns = loop.run()
    assert all(t.intent is Intent.UNKNOWN for t in turns)
    assert "did not catch" in tts.spoken[0]


def test_loop_stops_when_input_is_exhausted():
    loop, _ = _loop(["one thing", "two things"])
    turns = loop.run(max_turns=10)
    assert len(turns) == 2


def test_loop_respects_max_turns():
    loop, _ = _loop(["a", "b", "c", "d", "e"])
    assert len(loop.run(max_turns=2)) == 2


def test_turns_are_recorded_in_order():
    loop, _ = _loop([DUMP, "status"])
    loop.run()
    assert [t.intent for t in loop.turns] == [Intent.BRAIN_DUMP, Intent.STATUS]


def test_turn_serializes_to_json():
    import json

    loop, _ = _loop(["status"])
    loop.run()
    assert json.loads(json.dumps(loop.turns[0].to_dict()))["intent"] == "status"


def test_energy_setting_changes_what_gets_suggested():
    dump = "brain dump: write the OS assignment due today. send an email"

    low, _ = _loop([dump, "what should I do"], energy=Energy.LOW)
    low.run()
    high, _ = _loop([dump, "what should I do"], energy=Energy.HIGH)
    high.run()

    assert "email" in low.intake.pick(Energy.LOW).raw.lower()
    assert "assignment" in high.intake.pick(Energy.HIGH).raw.lower()


def test_quit_exits_instead_of_being_captured_as_a_task():
    """Regression: 'quit' used to route to UNKNOWN and become a task."""
    loop, tts = _loop(["brain dump: write the report", "quit"])
    turns = loop.run(max_turns=10)

    assert turns[-1].intent is Intent.QUIT
    assert len(turns) == 2, "the loop must stop on quit"
    assert all("quit" not in i.title.lower() for i in loop.intake.items)
    assert len(loop.intake.items) == 1


@pytest.mark.parametrize("word", ["quit", "exit", "stop", "goodbye", "bye", "that's all"])
def test_quit_synonyms_are_recognised(word):
    assert route(word) is Intent.QUIT


def test_quit_does_not_match_a_sentence_containing_the_word():
    assert route("quit worrying about the exam") is not Intent.QUIT


def test_quit_reports_how_much_is_saved():
    loop, tts = _loop(["brain dump: write the report. pay rent", "quit"])
    loop.run()
    assert "2 open items" in tts.spoken[-1]


def test_loop_works_without_an_event_bus(monkeypatch):
    """The policy gate is a nice-to-have; the loop must run without it."""
    import builtins

    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if "event_bus" in name or "voice_gateway" in name:
            raise ImportError("simulated missing dependency")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    loop = VoiceAgentLoop(stt=ConsoleInput(lines=["rm -rf /"]), tts=ConsoleOutput())
    turns = loop.run()
    # Without the gateway there is no policy engine, so it is captured instead
    # of blocked — the important thing is that it does not crash or execute.
    assert len(turns) == 1


# --------------------------------------------------------------------------- #
# The artifact gate: personal tasks must never reach the coding agent
# --------------------------------------------------------------------------- #


def test_personal_tasks_are_not_handed_to_the_agent():
    # "write", "fix" and "make" are the most common verbs in an ADHD brain dump.
    # Routing these to a coding agent does not just fail to help, it silently
    # destroys the task: the user believes it is safely on their list.
    for text in ["write the assignment", "fix the sink", "make the appointment"]:
        assert route(text) in (Intent.BRAIN_DUMP, Intent.UNKNOWN), text


def test_real_build_requests_still_reach_the_agent():
    for text in [
        "write a script that dedupes csv",
        "build a csv deduplicator",
        "fix the bug in my parser",
        "refactor the auth module",
        "write tests for the api",
    ]:
        assert route(text) is Intent.DO_WORK, text


def test_ambiguous_speech_is_captured_not_dropped():
    loop = VoiceAgentLoop(stt=ConsoleInput(lines=["pay the bill"]), tts=ConsoleOutput())
    turn = loop.listen_once()
    assert turn.intent is Intent.UNKNOWN
    assert len(loop.intake.items) == 1
    assert loop.intake.items[0].title.lower() == "pay the bill"
