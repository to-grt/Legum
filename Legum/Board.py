# Board.py

# Imports
import numpy as np
from Legum.Pieces.Piece import Piece
from Legum.Pieces.King import King
from Legum.Pieces.Queen import Queen
from Legum.Pieces.Rook import Rook
from Legum.Pieces.Bishop import Bishop
from Legum.Pieces.Knight import Knight
from Legum.Pieces.Pawn import Pawn

from Legum.constants import TYPE_COLORS, EMPTY, BOARD_SHAPE


class Board:

    def __init__(self) -> None:
        self.board = np.empty(shape=(8, 8))

    def set_to_default(self) -> None:
        self.board = np.array([
            [Rook(2, (0, 0)), Knight(2, (0, 1)), Bishop(2, (0, 2)), Queen(2, (0, 3)), King(2, (0, 4)), Bishop(2, (0, 5)), Knight(2, (0, 6)), Rook(2, (0, 7))],
            [Pawn(2, (1, 0)), Pawn(2, (1, 1)), Pawn(2, (1, 2)), Pawn(2, (1, 3)), Pawn(2, (1, 4)), Pawn(2, (1, 5)), Pawn(2, (1, 6)), Pawn(2, (1, 7))],
            [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [Pawn(1, (6, 0)), Pawn(1, (6, 1)), Pawn(1, (6, 2)), Pawn(1, (6, 3)), Pawn(1, (6, 4)), Pawn(1, (6, 5)), Pawn(1, (6, 6)), Pawn(1, (6, 7))],
            [Rook(1, (7, 0)), Knight(1, (7, 1)), Bishop(1, (7, 2)), Queen(1, (7, 3)), King(1, (7, 4)), Bishop(1, (7, 5)), Knight(1, (7, 6)), Rook(1, (7, 7))]
        ])

    def set_to_empty(self) -> None:
        self.board = np.empty(shape=BOARD_SHAPE)

    def get_masked_board(self) -> np.ndarray:
        return np.where(self.board == 0, 0, 1)

    def get_masked_board_for_color(self, color: TYPE_COLORS) -> np.ndarray:
        """
        Returns a masked board with 1 for pieces of the given color and 0 for the rest.
        """
        mask = np.zeros(BOARD_SHAPE, dtype=TYPE_COLORS)
        for index, piece in np.ndenumerate(self.board):
            if isinstance(piece, Piece):
                if piece.color == color:
                    mask[index] = color
        return mask

    def get_masked_board_with_colors(self) -> np.ndarray:
        """
        Returns a masked board with 1 for white pieces and 2 for black pieces.
        """
        mask = np.zeros(BOARD_SHAPE, dtype=int)
        for index, piece in np.ndenumerate(self.board):
            if isinstance(piece, Piece):
                mask[index] = piece.color
        return mask



