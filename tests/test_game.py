import random

import pytest

from legum.components import Color, Queen
from legum.game import STARTING_FEN, GameState, Move, perft

KIWIPETE = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
POSITION_3 = "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"
POSITION_4 = "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"
POSITION_5 = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"

# Reference values: https://www.chessprogramming.org/Perft_Results
# (also re-computed with python-chess when these tests were written)
PERFT_FAST = [
    (STARTING_FEN, [20, 400, 8902]),
    (KIWIPETE, [48, 2039]),
    (POSITION_3, [14, 191, 2812]),
    (POSITION_4, [6, 264]),
    (POSITION_5, [44, 1486]),
]
PERFT_SLOW = [
    (STARTING_FEN, 4, 197281),
    (KIWIPETE, 3, 97862),
    (POSITION_3, 4, 43238),
    (POSITION_4, 3, 9467),
    (POSITION_5, 3, 62379),
]


@pytest.mark.parametrize("fen, expected", PERFT_FAST)
def test_perft(fen, expected):
    state = GameState(fen)
    assert [perft(state, depth) for depth in range(1, len(expected) + 1)] == expected
    assert state.fen() == fen  # make/unmake leave the position untouched


@pytest.mark.slow
@pytest.mark.parametrize("fen, depth, expected", PERFT_SLOW)
def test_perft_deep(fen, depth, expected):
    assert perft(GameState(fen), depth) == expected


@pytest.mark.parametrize("fen", [STARTING_FEN, KIWIPETE, POSITION_3, POSITION_4, POSITION_5,
                                 "rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3"])
def test_fen_round_trip(fen):
    assert GameState(fen).fen() == fen


@pytest.mark.parametrize("fen", [
    "8/8/8/8/8/8/8/8 w - - 0 1",                                 # No kings
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR x KQkq - 0 1",  # Bad side to move
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP w KQkq - 0 1",           # Missing row
])
def test_invalid_fen(fen):
    with pytest.raises(ValueError):
        GameState(fen)


def test_board_reset_board():
    state = GameState("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    state.board.reset_board()
    assert state.board.placement() == STARTING_FEN.split()[0]


def test_uci_conversion():
    move = Move.from_uci("e7e8q")
    assert move == Move((1, 4), (0, 4), "Q")
    assert move.uci == "e7e8q"


def test_play_rejects_illegal_moves():
    state = GameState()
    with pytest.raises(ValueError):
        state.play("e2e5")
    state.play("e2e4")
    assert state.turn is Color.BLACK
    assert state.fen() == "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"


def test_en_passant_capture_and_undo():
    state = GameState("rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3")
    state.play("e5f6")
    assert state.board[3, 5] is None  # The black pawn on f5 is gone
    state.unmake_move()
    assert state.fen() == "rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3"


def test_promotion_and_undo():
    fen = "8/P6k/8/8/8/8/8/K7 w - - 0 1"
    state = GameState(fen)
    assert {move.promotion for move in state.legal_moves() if move.start == (1, 0)} == {"Q", "R", "B", "N"}
    state.play("a7a8q")
    assert isinstance(state.board[0, 0], Queen)
    state.unmake_move()
    assert state.fen() == fen


def test_castling_and_undo():
    fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
    state = GameState(fen)
    state.play("e1g1")
    assert state.board[7, 5].short_name == "R" and state.board[7, 6].short_name == "K"
    assert state.castling == "kq"
    state.unmake_move()
    assert state.fen() == fen


def test_cannot_castle_through_check():
    # The black rook on f8 attacks f1: white cannot castle king side, queen side is fine
    state = GameState("r4rk1/8/8/8/8/8/8/R3K2R w KQ - 0 1")
    moves = {move.uci for move in state.legal_moves()}
    assert "e1g1" not in moves and "e1c1" in moves


def test_capturing_a_rook_removes_castling_right():
    state = GameState("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    state.play("a1a8")
    assert state.castling == "Kk"


def test_checkmate():
    state = GameState()
    for move in ["f2f3", "e7e5", "g2g4", "d8h4"]:  # Fool's mate
        state.play(move)
    assert state.is_checkmate()
    outcome = state.outcome()
    assert outcome.result == "0-1" and outcome.reason == "checkmate" and outcome.winner is Color.BLACK


def test_stalemate():
    state = GameState("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    assert state.is_stalemate()
    assert state.outcome().reason == "stalemate"


@pytest.mark.parametrize("fen, expected", [
    ("8/8/4k3/8/8/4K3/8/8 w - - 0 1", True),     # K vs K
    ("8/8/4k3/8/8/4K3/5N2/8 w - - 0 1", True),   # K+N vs K
    ("8/2b5/4k3/8/8/4K3/5B2/8 w - - 0 1", True),  # Bishops on the same square color
    ("8/3b4/4k3/8/8/4K3/5B2/8 w - - 0 1", False),  # Bishops on different square colors
    ("8/8/4k3/8/8/4K3/4NN2/8 w - - 0 1", False),  # Two knights: mate is possible (with help)
    ("8/8/4k3/8/8/4K3/4P3/8 w - - 0 1", False),
])
def test_insufficient_material(fen, expected):
    assert GameState(fen).is_insufficient_material() is expected


def test_fifty_move_rule():
    state = GameState("8/8/4k3/8/8/4K3/4R3/8 w - - 99 80")
    state.play("e2e1")
    assert state.outcome().reason == "fifty-move rule"


def test_threefold_repetition():
    state = GameState()
    for _ in range(2):
        for move in ["g1f3", "g8f6", "f3g1", "f6g8"]:
            state.play(move)
    assert state.is_threefold_repetition()
    assert state.outcome().reason == "threefold repetition"


def _compare_random_games_with_python_chess(games, max_plies, seed):
    chess = pytest.importorskip("chess")
    rng = random.Random(seed)
    for _ in range(games):
        ours, reference = GameState(), chess.Board()
        for _ in range(max_plies):
            our_moves = sorted(move.uci for move in ours.legal_moves())
            assert our_moves == sorted(move.uci() for move in reference.legal_moves), ours.fen()
            # Like the FEN standard, we always write the en passant square after a double step;
            # python-chess only does so by default when the capture is legal
            assert ours.fen() == reference.fen(en_passant="fen")
            assert ours.in_check() == reference.is_check()
            assert ours.is_insufficient_material() == reference.is_insufficient_material()
            if not our_moves:
                break
            uci = rng.choice(our_moves)
            ours.play(uci)
            reference.push_uci(uci)


def test_random_games_match_python_chess():
    _compare_random_games_with_python_chess(games=5, max_plies=150, seed=0)


@pytest.mark.slow
def test_many_random_games_match_python_chess():
    _compare_random_games_with_python_chess(games=100, max_plies=300, seed=1)
