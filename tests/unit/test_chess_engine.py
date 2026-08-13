"""Unit tests for ChessGame Engine and DynamicOrchestrator integration in Jarvis X."""

import pytest
from jarvisx.games.chess_engine import ChessGame, get_or_create_chess_game
from jarvisx.automation.dynamic_orchestrator import DynamicOrchestrator


def test_chess_initial_board_render():
    game = ChessGame()
    rendered = game.render_board()
    assert "♙" in rendered or "P" in rendered
    assert "a   b   c   d   e   f   g   h" in rendered


def test_chess_user_and_alfred_moves():
    game = ChessGame()
    res = game.make_user_move("e2e4")
    assert res["status"] == "SUCCESS"
    assert "e2->e4" in res["move"]
    assert game.turn == "black"

    # Alfred AI move
    ai_res = game.alfred_ai_move()
    assert ai_res["status"] == "SUCCESS"
    assert game.turn == "white"
    assert "commentary" in ai_res


def test_dynamic_orchestrator_chess_intent():
    orch = DynamicOrchestrator()
    start_res = orch._execute_single_voice_command("play chess with me")
    assert start_res["action"] == "chess_start"
    assert "chess board is prepared" in start_res["response"]

    move_res = orch._execute_single_voice_command("move e4")
    assert move_res["action"] == "chess_move"
    assert "e2->e4" in move_res["response"] or "e2" in move_res["response"]
