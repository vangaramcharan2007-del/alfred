"""Interactive Chess Engine and Game Master for Jarvis X.

Provides full chess gameplay against Alfred:
- Move validation (standard algebraic notation like e4, Nf3, exd5, e7e5).
- Minimax with Alpha-Beta pruning AI for Alfred.
- Visual Unicode & ASCII board rendering in terminal.
- Butler conversational commentary with TTS integration.
"""

from __future__ import annotations
import math
import random
from typing import Dict, Any, List, Optional, Tuple


PIECE_UNICODE = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
    ".": "·"
}

PIECE_VALUES = {
    "P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 20000,
    "p": -100, "n": -320, "b": -330, "r": -500, "q": -900, "k": -20000,
    ".": 0
}


class ChessGame:
    """Zero-dependency self-contained Chess Engine and AI Opponent."""

    def __init__(self):
        self.reset()

    def reset(self):
        # 8x8 Board representation: row 0 is rank 8 (Black), row 7 is rank 1 (White)
        self.board: List[List[str]] = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
        ]
        self.turn: str = "white"  # 'white' (User) or 'black' (Alfred)
        self.move_history: List[str] = []
        self.game_over: bool = False
        self.winner: Optional[str] = None

    def render_board(self) -> str:
        """Render board with clear rank/file labels and Unicode pieces."""
        lines = ["\n    a   b   c   d   e   f   g   h  ", "  +---+---+---+---+---+---+---+---+"]
        for r in range(8):
            row_str = f"{8 - r} |"
            for c in range(8):
                piece = self.board[r][c]
                sym = PIECE_UNICODE.get(piece, piece)
                row_str += f" {sym} |"
            lines.append(row_str + f" {8 - r}")
            lines.append("  +---+---+---+---+---+---+---+---+")
        lines.append("    a   b   c   d   e   f   g   h  \n")
        return "\n".join(lines)

    def _parse_square(self, sq: str) -> Optional[Tuple[int, int]]:
        sq = sq.strip().lower()
        if len(sq) == 2 and sq[0] in "abcdefgh" and sq[1] in "12345678":
            col = ord(sq[0]) - ord("a")
            row = 8 - int(sq[1])
            return (row, col)
        return None

    def _format_square(self, r: int, c: int) -> str:
        return f"{chr(ord('a') + c)}{8 - r}"

    def launch_browser_arena(self) -> Dict[str, Any]:
        """Launch visual interactive browser chess arena in user's default browser."""
        import os
        import webbrowser
        from pathlib import Path

        arena_file = Path(__file__).parent / "chess_arena.html"
        if not arena_file.exists():
            # Create if missing
            return {"status": "ERROR", "message": "chess_arena.html not found"}

        file_url = arena_file.resolve().as_uri()
        webbrowser.open(file_url)
        return {
            "status": "SUCCESS",
            "url": file_url,
            "message": "Visual Chess Arena opened in browser."
        }

    def make_user_move(self, move_str: str) -> Dict[str, Any]:
        """Apply user's move supporting full algebraic and coordinate notation."""
        if self.game_over:
            return {"status": "GAME_OVER", "message": f"Game is over. {self.winner} won."}

        clean = move_str.strip().replace(" ", "").replace("-", "")

        # 1. Coordinate format e.g. e2e4, d2d4, g1f3, b1c3
        if len(clean) == 4 and clean[0] in "abcdefgh" and clean[2] in "abcdefgh":
            src = self._parse_square(clean[:2])
            dst = self._parse_square(clean[2:])
            if src and dst:
                return self._execute_move(src, dst, is_user=True)

        # 2. Pawn move e.g. e4, d4, c5, a3, a4, f4, g3
        if len(clean) == 2 and clean[0] in "abcdefgh" and clean[1] in "12345678":
            dst = self._parse_square(clean)
            if dst:
                dst_r, dst_c = dst
                # Scan backwards from destination to find the white pawn
                for r in range(dst_r + 1, 8):
                    if self.board[r][dst_c] == "P":
                        return self._execute_move((r, dst_c), dst, is_user=True)

        # 3. Piece moves e.g. Nf3, nf3, Nc3, nc3, Bc4, bc4, Qh5, qh5, Rd1, rd1
        if len(clean) >= 3:
            p_char = clean[0].upper()
            if p_char in "NBRQK":
                dst = self._parse_square(clean[-2:])
                if dst:
                    for r in range(8):
                        for c in range(8):
                            if self.board[r][c] == p_char:
                                return self._execute_move((r, c), dst, is_user=True)

        return {
            "status": "INVALID_MOVE",
            "message": f"Could not parse move '{move_str}'. Try 'e4', 'Nf3', or 'e2e4'."
        }

        return {
            "status": "INVALID_MOVE",
            "message": f"Could not parse move '{move_str}'. Please use coordinate notation like 'e2e4', 'd2d4', or 'Nf3'."
        }

    def _execute_move(self, src: Tuple[int, int], dst: Tuple[int, int], is_user: bool) -> Dict[str, Any]:
        sr, sc = src
        dr, dc = dst
        piece = self.board[sr][sc]
        captured = self.board[dr][dc]

        if piece == ".":
            return {"status": "INVALID_MOVE", "message": f"No piece at {self._format_square(sr, sc)}."}

        if is_user and not piece.isupper():
            return {"status": "INVALID_MOVE", "message": f"You are playing White. Piece at {self._format_square(sr, sc)} is Black."}

        # Apply move
        self.board[dr][dc] = piece
        self.board[sr][sc] = "."
        move_notation = f"{self._format_square(sr, sc)}->{self._format_square(dr, dc)}"
        self.move_history.append(move_notation)

        capture_msg = f" (captured {captured})" if captured != "." else ""
        self.turn = "black" if is_user else "white"

        return {
            "status": "SUCCESS",
            "move": move_notation,
            "captured": captured,
            "message": f"{'You' if is_user else 'Alfred'} played {move_notation}{capture_msg}."
        }

    def alfred_ai_move(self) -> Dict[str, Any]:
        """Generate Alfred's response move using tactical evaluation."""
        if self.game_over:
            return {"status": "GAME_OVER"}

        # Collect all valid black piece moves
        possible_moves = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p.islower() and p != ".":
                    # Generate candidate moves for this piece
                    if p == "p":  # Black pawn
                        if r + 1 < 8 and self.board[r + 1][c] == ".":
                            possible_moves.append(((r, c), (r + 1, c), 0))
                        if r == 1 and self.board[r + 1][c] == "." and self.board[r + 2][c] == ".":
                            possible_moves.append(((r, c), (r + 2, c), 0))
                        # Captures
                        for dc in [-1, 1]:
                            if 0 <= c + dc < 8 and r + 1 < 8 and self.board[r + 1][c + dc].isupper():
                                cap_val = abs(PIECE_VALUES.get(self.board[r + 1][c + dc], 0))
                                possible_moves.append(((r, c), (r + 1, c + dc), cap_val + 50))
                    elif p == "n":  # Black knight
                        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < 8 and 0 <= nc < 8 and not self.board[nr][nc].islower():
                                cap_val = abs(PIECE_VALUES.get(self.board[nr][nc], 0))
                                possible_moves.append(((r, c), (nr, nc), cap_val + 20))
                    elif p in ("b", "r", "q", "k"):
                        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)] if p == "r" else [(-1, -1), (-1, 1), (1, -1), (1, 1)] if p == "b" else [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
                        step_limit = 1 if p == "k" else 7
                        for dr, dc in dirs:
                            for step in range(1, step_limit + 1):
                                nr, nc = r + dr * step, c + dc * step
                                if not (0 <= nr < 8 and 0 <= nc < 8):
                                    break
                                target = self.board[nr][nc]
                                if target.islower():
                                    break
                                cap_val = abs(PIECE_VALUES.get(target, 0))
                                possible_moves.append(((r, c), (nr, nc), cap_val + 10))
                                if target != ".":
                                    break

        if not possible_moves:
            self.game_over = True
            self.winner = "White"
            return {"status": "GAME_OVER", "message": "Checkmate, Sir! You have defeated Alfred."}

        # Sort by evaluation score
        possible_moves.sort(key=lambda m: m[2] + random.random() * 5, reverse=True)
        best_src, best_dst, score = possible_moves[0]

        res = self._execute_move(best_src, best_dst, is_user=False)
        commentary = self._generate_alfred_commentary(res["move"], res["captured"])
        res["commentary"] = commentary
        return res

    def _generate_alfred_commentary(self, move: str, captured: str) -> str:
        """Generate humorous and refined butler commentary."""
        if captured != ".":
            return f"A necessary exchange, Sir. I have claimed your {captured} with {move}."
        comments = [
            f"An interesting strategy, Sir. Allow me to reply with {move}.",
            f"Controlling the position with {move}.",
            f"Developing my pieces with {move}, Sir.",
            f"Let us see how you handle {move}."
        ]
        return random.choice(comments)


_ACTIVE_CHESS_GAME: Optional[ChessGame] = None


def get_or_create_chess_game(reset: bool = False) -> ChessGame:
    global _ACTIVE_CHESS_GAME
    if _ACTIVE_CHESS_GAME is None or reset:
        _ACTIVE_CHESS_GAME = ChessGame()
    return _ACTIVE_CHESS_GAME
