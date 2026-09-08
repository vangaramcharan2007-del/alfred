"""Tests for the ADHD-oriented task intake engine."""

from __future__ import annotations

import pytest

from jarvisx.agentic.intake import (
    CapturedItem,
    Energy,
    IntakeEngine,
    ItemKind,
    breakdown,
    classify,
    next_action,
    split_brain_dump,
)

BRAIN_DUMP = (
    "um ok so i need to write the OS assignment its due today, "
    "also reply to that email from the professor, "
    "oh and i'm really worried about failing this semester, "
    "someone should really fix the lab printer, "
    "someday it would be cool to build a voice assistant, "
    "and i gotta pay the electricity bill"
)


# --------------------------------------------------------------------------- #
# Splitting
# --------------------------------------------------------------------------- #


def test_split_brain_dump_separates_all_six_items():
    items = split_brain_dump(BRAIN_DUMP)
    assert len(items) == 6
    assert any("OS assignment" in i for i in items)
    assert any("electricity bill" in i for i in items)


def test_split_brain_dump_strips_filler_words():
    items = split_brain_dump("um, so, basically I need to call the bank")
    assert len(items) == 1
    lowered = items[0].lower()
    for filler in ("um", "so", "basically"):
        assert not lowered.startswith(filler)


def test_split_brain_dump_splits_on_newlines():
    assert len(split_brain_dump("pay rent\nbook dentist\nemail sam")) == 3


def test_split_brain_dump_splits_on_semicolons():
    assert len(split_brain_dump("pay rent; book dentist; email sam")) == 3


def test_split_brain_dump_splits_after_sentence_ends():
    assert len(split_brain_dump("Pay the rent. Book the dentist.")) == 2


def test_split_brain_dump_discards_tiny_fragments():
    assert split_brain_dump("ok. and. um. pay the rent") == ["pay the rent"]


def test_split_brain_dump_handles_empty_input():
    assert split_brain_dump("") == []
    assert split_brain_dump("   \n  ") == []


def test_split_brain_dump_collapses_internal_whitespace():
    # Single line: newlines are deliberate separators, so use spaces here.
    assert split_brain_dump("pay    the    rent") == ["pay the rent"]


def test_split_brain_dump_treats_newlines_as_separators():
    assert split_brain_dump("pay the\nrent") == ["pay the", "rent"]


# --------------------------------------------------------------------------- #
# Classification
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "text,expected",
    [
        ("write the OS assignment", ItemKind.TASK),
        ("pay the electricity bill", ItemKind.TASK),
        ("I'm really worried about failing this semester", ItemKind.WORRY),
        ("I dread the presentation", ItemKind.WORRY),
        ("what if I never finish", ItemKind.WORRY),
        ("someone should really fix the lab printer", ItemKind.DELEGATE),
        ("ask Ravi to send the notes", ItemKind.DELEGATE),
        ("this is not my job", ItemKind.DELEGATE),
        ("someday it would be cool to build an assistant", ItemKind.IDEA),
        ("what if we built a mesh network", ItemKind.IDEA),
        ("how do I rotate a matrix", ItemKind.QUESTION),
        ("what is the deadline policy?", ItemKind.QUESTION),
    ],
)
def test_classify(text, expected):
    assert classify(text) is expected


def test_replying_to_an_email_is_a_task_not_delegation():
    """Regression: the old delegate pattern matched the bare word 'email'."""
    assert classify("reply to that email from the professor") is ItemKind.TASK


def test_worry_takes_priority_over_task_words():
    assert classify("I'm stressed about the report I need to write") is ItemKind.WORRY


# --------------------------------------------------------------------------- #
# Next actions
# --------------------------------------------------------------------------- #


def test_next_action_is_physical_and_small_for_tasks():
    assert next_action("write the report") == "Open the file and write one heading"
    assert next_action("call the bank") == "Find the number and dial it"
    assert next_action("clean my desk") == "Set a 10-minute timer and do one surface"


def test_next_action_for_non_tasks_tells_you_to_stop():
    assert "Not a task" in next_action("worried about exams", ItemKind.WORRY)
    assert "Not a task" in next_action("cool idea someday", ItemKind.IDEA)
    assert "one message" in next_action("ask Ravi for notes", ItemKind.DELEGATE)
    assert "wait" in next_action("how do I do X", ItemKind.QUESTION)


def test_next_action_has_a_generic_fallback():
    assert "first two minutes" in next_action("do the mysterious thing")


def test_breakdown_first_step_is_always_trivial():
    steps = breakdown("write the essay")
    assert steps
    assert "heading" in steps[0]
    assert len(steps) <= 3


def test_breakdown_respects_the_step_limit():
    assert len(breakdown("write the essay", steps=2)) == 2
    assert len(breakdown("write the essay", steps=1)) == 1


def test_breakdown_of_a_non_task_is_a_single_step():
    assert breakdown("someday build a robot") == [
        next_action("someday build a robot", ItemKind.IDEA)
    ]


# --------------------------------------------------------------------------- #
# Engine: capture
# --------------------------------------------------------------------------- #


def test_capture_classifies_every_item_in_a_brain_dump():
    engine = IntakeEngine()
    captured = engine.capture(BRAIN_DUMP)
    kinds = [i.kind for i in captured]
    assert kinds.count(ItemKind.TASK) == 3
    assert ItemKind.WORRY in kinds
    assert ItemKind.DELEGATE in kinds
    assert ItemKind.IDEA in kinds


def test_capture_detects_urgency_from_deadline_words():
    engine = IntakeEngine()
    captured = engine.capture("write the OS assignment its due today. read a book someday")
    urgent = next(i for i in captured if "assignment" in i.raw)
    calm = next(i for i in captured if "book" in i.raw)
    assert urgent.urgency == 5
    assert calm.urgency == 1


def test_capture_estimates_effort_and_under_promise_is_avoided():
    engine = IntakeEngine()
    captured = engine.capture(
        "build a full project. send an email. take 15 minutes to stretch"
    )
    project = next(i for i in captured if "project" in i.raw)
    email = next(i for i in captured if "email" in i.raw)
    explicit = next(i for i in captured if "stretch" in i.raw)
    assert project.est_minutes >= 45, "project work must not look cheap"
    assert email.est_minutes <= 10
    assert explicit.est_minutes == 15, "an explicit estimate wins"


def test_capture_tags_by_domain():
    engine = IntakeEngine()
    captured = engine.capture("study for the exam. pay the rent")
    assert "study" in captured[0].tags
    assert "money" in captured[1].tags


def test_capture_marks_already_done_items():
    engine = IntakeEngine()
    captured = engine.capture("I already paid the rent")
    assert captured[0].done is True
    assert engine.open_items == []


def test_capture_of_empty_input_creates_nothing():
    engine = IntakeEngine()
    assert engine.capture("") == []
    assert engine.items == []


def test_title_strips_modals_but_raw_is_preserved():
    engine = IntakeEngine()
    item = engine.capture("I need to write the report")[0]
    assert item.title == "Write the report"
    assert item.raw == "I need to write the report"


# --------------------------------------------------------------------------- #
# Engine: selection
# --------------------------------------------------------------------------- #


def test_low_energy_picks_the_small_task_not_the_urgent_big_one():
    """The core ADHD behaviour: do not hand a tired brain a 45-minute task."""
    engine = IntakeEngine()
    engine.capture(
        "write the OS assignment due today. reply to that email from the professor"
    )
    pick = engine.pick(Energy.LOW)
    assert pick is not None
    assert "email" in pick.raw.lower()
    assert pick.est_minutes <= 10


def test_high_energy_picks_the_urgent_task():
    engine = IntakeEngine()
    engine.capture(
        "write the OS assignment due today. reply to that email from the professor"
    )
    pick = engine.pick(Energy.HIGH)
    assert "assignment" in pick.raw.lower()


def test_pick_respects_minutes_available():
    engine = IntakeEngine()
    engine.capture("write the report. send an email")
    pick = engine.pick(Energy.HIGH, minutes_available=8)
    assert "email" in pick.raw.lower()


def test_pick_never_returns_a_worry_idea_or_delegation():
    engine = IntakeEngine()
    engine.capture(
        "worried about exams. someday build a robot. ask Ravi to help. write the report"
    )
    pick = engine.pick(Energy.HIGH)
    assert pick is not None and pick.kind is ItemKind.TASK


def test_pick_returns_none_when_only_non_tasks_remain():
    engine = IntakeEngine()
    engine.capture("worried about exams. someday build a robot")
    assert engine.pick(Energy.HIGH) is None


def test_pick_falls_back_to_the_smallest_task_when_nothing_fits():
    engine = IntakeEngine()
    engine.capture("rebuild the entire project")
    pick = engine.pick(Energy.LOW)  # 90-min task, 10-min ceiling
    assert pick is not None, "must still suggest something rather than nothing"


def test_pick_ignores_completed_items():
    engine = IntakeEngine()
    items = engine.capture("send an email. write the report")
    engine.complete(items[0].id)
    pick = engine.pick(Energy.HIGH)
    assert "report" in pick.raw.lower()


def test_complete_reports_unknown_ids():
    engine = IntakeEngine()
    assert engine.complete("nope") is False


# --------------------------------------------------------------------------- #
# Engine: plan + persistence
# --------------------------------------------------------------------------- #


def test_plan_returns_a_single_next_action_and_steps():
    engine = IntakeEngine()
    plan = engine.plan(BRAIN_DUMP, energy=Energy.LOW)
    assert plan["do_this_next"] is not None
    assert plan["steps"]
    assert plan["energy"] == "low"
    assert plan["counts"]["worry"] == 1
    assert len(plan["not_your_problem"]) == 2


def test_plan_of_nothing_is_honest():
    engine = IntakeEngine()
    plan = engine.plan("   ", energy=Energy.LOW)
    assert plan["do_this_next"] is None
    assert plan["steps"] == []


def test_round_trip_persistence():
    engine = IntakeEngine()
    engine.capture(BRAIN_DUMP)
    payload = engine.to_dict()

    restored = IntakeEngine()
    restored.load(payload)
    assert len(restored.items) == len(engine.items)
    assert restored.pick(Energy.LOW).id == engine.pick(Energy.LOW).id


def test_captured_item_serializes_kind_as_a_string():
    item = CapturedItem(id="x", title="t", raw="r", kind=ItemKind.WORRY)
    assert item.to_dict()["kind"] == "worry"


# --------------------------------------------------------------------------- #
# Comma splitting: a blob is the thing an ADHD brain cannot start
# --------------------------------------------------------------------------- #


def test_comma_separated_verbs_split_into_separate_tasks():
    parts = split_brain_dump("write the assignment, pay the bill, call mom")
    assert len(parts) == 3, parts
    assert parts == ["write the assignment", "pay the bill", "call mom"]


def test_splitting_on_a_comma_never_shreds_a_qualifier():
    # "the professor" is not a verb, so this stays one item. Splitting on every
    # comma would turn this into two broken fragments.
    parts = split_brain_dump("reply to the email from Dave, the professor")
    assert len(parts) == 1, parts


def test_a_shopping_list_stays_one_item():
    assert len(split_brain_dump("buy milk, eggs and bread")) == 1


def test_three_item_blob_becomes_three_pickable_tasks():
    engine = IntakeEngine()
    engine.plan("write the assignment, pay the bill, call mom")
    tasks = [i for i in engine.open_items if i.kind is ItemKind.TASK]
    assert len(tasks) == 3, tasks
    # The whole point: on low energy it offers something you can actually start.
    chosen = engine.pick(Energy.LOW)
    assert chosen is not None
    assert chosen.est_minutes <= 10, chosen
