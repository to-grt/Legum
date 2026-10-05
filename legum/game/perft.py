from typing import Dict

from .GameState import GameState


def perft(state: GameState, depth: int) -> int:
    """
    Counts the leaf nodes of the legal move tree at the given depth.
    The reference test for move generators: https://www.chessprogramming.org/Perft
    """
    if depth == 0:
        return 1
    moves = state.legal_moves()
    if depth == 1:
        return len(moves)
    nodes = 0
    for move in moves:
        state.make_move(move)
        nodes += perft(state, depth - 1)
        state.unmake_move()
    return nodes


def divide(state: GameState, depth: int) -> Dict[str, int]:
    """Perft split by first move, handy to find which move is generated wrongly."""
    result = {}
    for move in state.legal_moves():
        state.make_move(move)
        result[move.uci] = perft(state, depth - 1)
        state.unmake_move()
    return result
