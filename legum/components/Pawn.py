from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from .Color import Color
from .Piece import Piece

if TYPE_CHECKING:
    from .Board import Board


class Pawn(Piece):
    """
    A class to represent a Pawn chess piece.
    White pawns move towards row 0, black pawns towards the last row.
    Methods:
        find_moves(board, en_passant): Target squares, including the double step and the en passant capture.
            Promotion is handled by GameState when a target is on the last row.
    """

    name = "Pawn"
    short_name = "P"
    value = 100

    @property
    def forward(self) -> int:
        return -1 if self.color is Color.WHITE else 1

    def start_row(self, board_size: int) -> int:
        return board_size - 2 if self.color is Color.WHITE else 1

    def promotion_row(self, board_size: int) -> int:
        return 0 if self.color is Color.WHITE else board_size - 1

    def attacked_squares(self, board: Board) -> List[Tuple[int, int]]:
        row, col = self.position
        targets = [(row + self.forward, col - 1), (row + self.forward, col + 1)]
        return [target for target in targets if board.check_position(target)]

    def find_moves(self, board: Board, en_passant: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        if self.position is None:
            raise ValueError(f"{self!r} is not on the board.")
        possible_moves = []
        row, col = self.position
        one_step = (row + self.forward, col)
        if board.check_position(one_step) and board[one_step] is None:
            possible_moves.append(one_step)
            two_steps = (row + 2 * self.forward, col)
            if row == self.start_row(board.board_size) and board[two_steps] is None:
                possible_moves.append(two_steps)
        for target in self.attacked_squares(board):
            target_cell = board[target]
            if (target_cell is not None and target_cell.color != self.color) or target == en_passant:
                possible_moves.append(target)
        return possible_moves
