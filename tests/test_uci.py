import io
import sys
import time

import pytest

from legum.engine import MATE_SCORE
from legum.game import GameState, Move
from legum.uci import UCIEngine, format_score


def run_commands(*commands):
    """Runs the engine on a list of commands and returns its output lines."""
    output = io.StringIO()
    UCIEngine(output).run(io.StringIO("\n".join(commands) + "\n"))
    return output.getvalue().splitlines()


def bestmove(lines):
    return [line.split()[1] for line in lines if line.startswith("bestmove")]


def test_handshake():
    assert run_commands("uci", "isready", "quit") == [
        "id name Legum", "id author Legum contributors", "uciok", "readyok"]


def test_unknown_commands_are_ignored():
    assert run_commands("foo bar", "isready") == ["readyok"]


def test_go_depth_returns_a_legal_move_with_info_lines():
    lines = run_commands("position startpos moves e2e4 e7e5", "go depth 2", "isready")
    assert [line for line in lines if line.startswith("info depth")][-1].startswith("info depth 2 score cp")
    state = GameState()
    state.play("e2e4")
    state.play("e7e5")
    assert Move.from_uci(bestmove(lines)[0]) in state.legal_moves()


def test_finds_mate_in_one_from_fen():
    lines = run_commands("position fen r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 2 3",
                         "go depth 2", "isready")
    assert bestmove(lines) == ["h5f7"]
    assert any("score mate 1" in line for line in lines)


def test_null_move_when_the_game_is_over():
    lines = run_commands("position startpos moves f2f3 e7e5 g2g4 d8h4", "go depth 2", "isready")
    assert bestmove(lines) == ["0000"]


def test_invalid_position_is_reported_and_ignored():
    lines = run_commands("position startpos moves e2e5", "go depth 1", "isready")
    assert lines[0].startswith("info string invalid position")
    assert Move.from_uci(bestmove(lines)[0]) in GameState().legal_moves()


def test_stop_ends_an_infinite_search():
    output = io.StringIO()
    engine = UCIEngine(output)
    engine.handle("position startpos")
    engine.handle("go infinite")
    time.sleep(0.3)
    start = time.monotonic()
    engine.handle("stop")
    assert time.monotonic() - start < 5
    assert len(bestmove(output.getvalue().splitlines())) == 1


def test_movetime_is_respected():
    output = io.StringIO()
    engine = UCIEngine(output)
    start = time.monotonic()
    engine.handle("go movetime 300")
    engine.wait_search()
    assert time.monotonic() - start < 2
    assert len(bestmove(output.getvalue().splitlines())) == 1


def test_clock_based_time_budget():
    engine = UCIEngine(io.StringIO())
    depth, time_limit = engine.search_limits({"wtime": 60_000, "btime": 60_000, "winc": 1000}, infinite=False)
    assert time_limit == pytest.approx(60 / 30 + 0.8)
    _, time_limit = engine.search_limits({"wtime": 100, "btime": 60_000}, infinite=False)
    assert time_limit <= 0.05  # Never more than half of the remaining time


@pytest.mark.parametrize("score, expected", [
    (35, "cp 35"), (-120, "cp -120"),
    (MATE_SCORE - 1, "mate 1"), (MATE_SCORE - 3, "mate 2"), (-(MATE_SCORE - 2), "mate -1"),
])
def test_format_score(score, expected):
    assert format_score(score) == expected


def test_python_chess_can_drive_legum_as_a_uci_engine():
    chess_engine = pytest.importorskip("chess.engine")
    chess = pytest.importorskip("chess")
    with chess_engine.SimpleEngine.popen_uci([sys.executable, "-m", "legum.uci"]) as engine:
        assert engine.id["name"] == "Legum"
        board = chess.Board()
        for _ in range(4):
            result = engine.play(board, chess_engine.Limit(depth=1))
            assert result.move in board.legal_moves
            board.push(result.move)
        info = engine.analyse(chess.Board("r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 2 3"),
                              chess_engine.Limit(depth=2))
        assert info["score"].white() == chess_engine.Mate(1)


def test_quit_interrupts_a_running_search():
    start = time.monotonic()
    lines = run_commands("position startpos", "go infinite", "quit")
    assert time.monotonic() - start < 5
    assert len(bestmove(lines)) == 1
