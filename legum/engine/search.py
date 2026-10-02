import time
from dataclasses import dataclass
from typing import List, Optional

from legum.game import GameState, Move

from .evaluation import evaluate

MATE_SCORE = 100_000
INFINITY = 1_000_000


class SearchTimeout(Exception):
    pass


@dataclass
class SearchResult:
    move: Optional[Move]
    score: int  # Centipawns, side to move's point of view; |score| > MATE_SCORE - 1000 means a forced mate
    depth: int
    nodes: int


class Searcher:
    """
    Negamax search with alpha-beta pruning, quiescence search on captures and iterative deepening.
    Methods:
        search(state, depth, time_limit): Returns the best move found.
    """

    def __init__(self) -> None:
        self.nodes = 0
        self.deadline: Optional[float] = None

    def search(self, state: GameState, depth: int = 3, time_limit: Optional[float] = None) -> SearchResult:
        """
        Searches depth 1, 2, ... up to `depth`. With a `time_limit` (seconds), stops early and returns
        the result of the last fully searched depth.
        """
        self.nodes = 0
        self.deadline = time.monotonic() + time_limit if time_limit else None
        best = SearchResult(None, 0, 0, 0)
        moves = self.order_moves(state, state.legal_moves())
        if not moves:
            return best
        for current_depth in range(1, depth + 1):
            try:
                score, move = self._root(state, moves, current_depth)
            except SearchTimeout:
                break
            best = SearchResult(move, score, current_depth, self.nodes)
            # Search the best move first at the next depth: it makes alpha-beta cut much more
            moves.remove(move)
            moves.insert(0, move)
            if abs(score) > MATE_SCORE - 1000:
                break
        if best.move is None:  # Not even depth 1 finished in time
            best = SearchResult(moves[0], 0, 0, self.nodes)
        return best

    def _root(self, state: GameState, moves: List[Move], depth: int):
        alpha, beta = -INFINITY, INFINITY
        best_move = moves[0]
        for move in moves:
            state.make_move(move)
            try:
                score = -self.negamax(state, depth - 1, -beta, -alpha, ply=1)
            finally:
                state.unmake_move()
            if score > alpha:
                alpha, best_move = score, move
        return alpha, best_move

    def negamax(self, state: GameState, depth: int, alpha: int, beta: int, ply: int) -> int:
        self.nodes += 1
        if self.deadline is not None and self.nodes % 256 == 0 and time.monotonic() > self.deadline:
            raise SearchTimeout()
        if state.is_fifty_moves() or state.is_threefold_repetition() or state.is_insufficient_material():
            return 0

        moves = state.legal_moves()
        if not moves:
            # Prefer faster mates (and slower defeats) by counting the distance from the root
            return -(MATE_SCORE - ply) if state.in_check() else 0
        if depth <= 0:
            return self.quiescence(state, alpha, beta, ply)

        for move in self.order_moves(state, moves):
            state.make_move(move)
            try:
                score = -self.negamax(state, depth - 1, -beta, -alpha, ply + 1)
            finally:
                state.unmake_move()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def quiescence(self, state: GameState, alpha: int, beta: int, ply: int) -> int:
        """Only looks at captures and promotions, so that the evaluation is not taken in the middle of a trade."""
        self.nodes += 1
        stand_pat = evaluate(state)
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
        noisy = [move for move in state.legal_moves() if move.promotion or state.is_capture(move)]
        for move in self.order_moves(state, noisy):
            state.make_move(move)
            try:
                score = -self.quiescence(state, -beta, -alpha, ply + 1)
            finally:
                state.unmake_move()
            if score >= beta:
                return beta
            alpha = max(alpha, score)
        return alpha

    @staticmethod
    def order_moves(state: GameState, moves: List[Move]) -> List[Move]:
        """Most promising moves first: promotions, then captures of valuable pieces by cheap ones (MVV-LVA)."""
        def priority(move: Move) -> int:
            score = 0
            if move.promotion == "Q":
                score += 10_000
            target = state.board[move.end]
            if target is not None:
                score += 10 * target.value - state.board[move.start].value + 1_000
            elif state.is_capture(move):  # En passant
                score += 1_000
            return -score
        return sorted(moves, key=priority)


def find_best_move(state: GameState, depth: int = 3, time_limit: Optional[float] = None) -> Optional[Move]:
    return Searcher().search(state, depth, time_limit).move
