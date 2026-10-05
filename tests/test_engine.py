import random

import pytest

from legum.components import Color
from legum.engine import MATE_SCORE, Searcher, evaluate, find_best_move
from legum.game import GameState


def test_evaluation_is_symmetric_at_start():
    assert evaluate(GameState()) == 0


def test_evaluation_counts_material_for_side_to_move():
    # White is a queen up
    assert evaluate(GameState("4k3/8/8/8/8/8/8/3QK3 w - - 0 1")) > 800
    assert evaluate(GameState("4k3/8/8/8/8/8/8/3QK3 b - - 0 1")) < -800


def test_finds_mate_in_one():
    state = GameState("r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 2 3")
    result = Searcher().search(state, depth=2)
    assert result.move.uci == "h5f7"
    assert result.score > MATE_SCORE - 1000


def test_finds_back_rank_mate_in_two():
    # 1. Qd8+ Rxd8 2. Rxd8#
    state = GameState("2r3k1/5ppp/8/8/8/8/3Q1PPP/3R2K1 w - - 0 1")
    result = Searcher().search(state, depth=4)
    assert result.move.uci == "d2d8"
    assert result.score > MATE_SCORE - 1000


def test_takes_a_hanging_queen():
    state = GameState("4k3/8/8/3q4/8/8/8/3RK3 w - - 0 1")
    assert find_best_move(state, depth=2).uci == "d1d5"


def test_search_leaves_the_state_untouched():
    state = GameState()
    fen = state.fen()
    find_best_move(state, depth=2)
    assert state.fen() == fen and not state.history


def test_time_limit_still_returns_a_legal_move():
    state = GameState()
    move = find_best_move(state, depth=10, time_limit=0.05)
    assert move in state.legal_moves()


def _play_against_random(engine_color, depth, seed, max_plies=300):
    rng = random.Random(seed)
    state = GameState()
    for _ in range(max_plies):
        if state.outcome() is not None:
            break
        if state.turn is engine_color:
            state.make_move(find_best_move(state, depth=depth))
        else:
            state.make_move(rng.choice(state.legal_moves()))
    return state.outcome()


@pytest.mark.slow
@pytest.mark.parametrize("seed", range(4))
def test_engine_beats_a_random_player(seed):
    engine_color = Color.WHITE if seed % 2 == 0 else Color.BLACK
    outcome = _play_against_random(engine_color, depth=2, seed=seed)
    assert outcome is not None and outcome.winner is engine_color, outcome
