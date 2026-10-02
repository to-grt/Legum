from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from .Piece import Piece

if TYPE_CHECKING:
    from .Board import Board


class King(Piece):
    """
    A class to represent a King chess piece, inheriting from the Piece class.
    Methods:
        find_moves(board): Returns the squares the King can move to (empty or occupied by an opponent).
    """

    name = "King"
    short_name = "K"
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def find_moves(self, board: Board) -> List[Tuple[int, int]]:
        possible_moves = []
        row, col = self.position
        for d_row, d_col in self.directions:
            target = (row + d_row, col + d_col)
            if board.check_position(target):
                target_cell = board[target]
                if target_cell is None or target_cell.color != self.color:
                    possible_moves.append(target)
        return possible_moves
