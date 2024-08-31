# Bishop.py


# Imports
import numpy as np
from Legum.Pieces.Piece import Piece


class Bishop(Piece):
    """
    Class representing a bishop piece.
    """

    def __init__(self, color: int, position: tuple) -> None:
        super().__init__()
        self.name = "Bishop"
        self.color = color
        self.position = position
        self.is_alive = True
        self.has_move = False

    def __str__(self) -> str:
        return f"Bishop {self.color}"

    def __call__(self) -> list:
        return self.get_moves_from_direction_vectors()

    def get_moves_from_direction_vectors(self) -> list:
        vectors = np.arange(0, 8)
        return []