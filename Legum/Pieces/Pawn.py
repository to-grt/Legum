# Pawn.py


# Imports
from Legum.Pieces.Piece import Piece


class Pawn(Piece):
    """
    Class representing a pawn piece.
    """

    def __init__(self, color: int, position: tuple) -> None:
        super().__init__()
        self.name = "Pawn"
        self.color = color
        self.position = position
        self.is_alive = True
        self.has_move = False

    def __str__(self) -> str:
        return f"Pawn {self.color}"

    def __call__(self) -> list:
        return self.get_moves_from_absolute_vectors()

    def get_moves_from_absolute_vectors(self) -> list:
        vectors = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        moves = []
        for vector in vectors:
            move = (self.position[0] + vector[0], self.position[1] + vector[1])
            if 0 <= move[0] <= 7 and 0 <= move[1] <= 7:
                moves.append(move)
        return moves
