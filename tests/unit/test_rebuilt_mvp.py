"""
Unit Test Suite for Rebuilt Product MVP.
Tests Alfred MVP (im_back, fix_this, build_this), Friday Academic Engine (10 CGPA Strategy), and Second Brain.
"""
import pytest
import asyncio
from pathlib import Path

from jarvisx.cognition.alfred_mvp import AlfredMVP
from friday.academic_engine import FridayAcademicEngine
from jarvisx.memory.second_brain import SecondBrain
from jarvisx.interface.cli import JarvisCLI


def test_alfred_im_back(tmp_path):
    amvp = AlfredMVP()
    res = amvp.im_back(cwd=str(tmp_path))
    assert res["status"] == "SUCCESS"
    assert "branch" in res
    assert "recommended_next_task" in res


def test_alfred_fix_this(tmp_path):
    amvp = AlfredMVP()
    res = amvp.fix_this(cwd=str(tmp_path), max_retries=1)
    assert res["status"] in ("SUCCESS", "DIAGNOSED")


def test_alfred_build_this(tmp_path):
    amvp = AlfredMVP()
    res = amvp.build_this("Automated Test Suite", cwd=str(tmp_path))
    assert res["status"] == "SUCCESS"
    assert len(res["plan_steps"]) > 0


def test_friday_academic_engine():
    fae = FridayAcademicEngine()
    strat = fae.calculate_10_cgpa_strategy()
    assert strat["target_cgpa"] == 10.0
    assert strat["top_focus"] is not None

    directive = fae.generate_morning_academic_directive()
    assert directive["status"] == "SUCCESS"
    assert "directive_text" in directive


@pytest.mark.asyncio
async def test_second_brain_queries():
    sb = SecondBrain()
    res1 = await sb.answer_question("What were we doing?")
    assert res1["status"] == "SUCCESS"

    res2 = await sb.answer_question("Why did we choose FastAPI?")
    assert res2["status"] == "SUCCESS"

    res3 = await sb.answer_question("What assignment is most important?")
    assert res3["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_cli_mvp_commands():
    cli = JarvisCLI()

    res_back = await cli.handle_command_async("im-back")
    assert res_back["status"] == "SUCCESS"

    res_build = await cli.handle_command_async("build-this Quick API")
    assert res_build["status"] == "SUCCESS"

    res_ask = await cli.handle_command_async("ask Why did we choose FastAPI?")
    assert res_ask["status"] == "SUCCESS"
