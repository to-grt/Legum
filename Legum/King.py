# King.py


# Imports
from Legum.Piece import Piece


class King(Piece):
    """
    Class representing a king piece.
    """

    def __init__(self, color: int, position: tuple) -> None:
        super().__init__()
        self.name = "King"
        self.color = color
        self.position = position
        self.is_alive = True

    def __repr__(self) -> str:
        return f"<King {self.color} {self.position} {self.is_alive}>"

    def __str__(self) -> str:
        return f"King {self.color}"

    def __call__(self) -> list:
        return self.get_moves_from_absolute_vectors()

    def get_moves_from_absolute_vectors(self) -> list:
        vectors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        moves = []
        for vector in vectors:
            move = (self.position[0] + vector[0], self.position[1] + vector[1])
            if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                moves.append(move)
        return moves
