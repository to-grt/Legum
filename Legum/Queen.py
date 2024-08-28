# Queen.py


# Imports
import numpy as np
from Legum.Piece import Piece


class Queen(Piece):

    def __init__(self, color: int, position: tuple) -> None:
        super().__init__()
        self.name = "Queen"
        self.color = color
        self.position = position
        self.is_alive = True


    def __repr__(self) -> str:
        return f"<Knight {self.color} {self.position} {self.is_alive}>"

    def __str__(self) -> str:
        return f"Knight {self.color}"

    def __call__(self) -> str:
        return self.__str__()

    @staticmethod
    def get_direction_vectors() -> list:
        """
        Get the vectors of the possible moves of the knight on the board.
        """
        return [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def get_moves_from_directions(self) -> list:
        """
        Get the destination squares of the knight on the board. Color is not taken into account because
        the moves are the same independently of the color of the piece.
        TODO: will be updated to take into account the whole board, and especially the other pieces.
        """
        vectors = self.get_direction_vectors()
        moves = []
        for vector in vectors:

            pass

        return moves

    def move(self, position: tuple) -> None:
        """
        Move the knight to the given position.
        """
        super().move(position)

    def dies(self) -> None:
        """
        Set the piece as dead.
        """
        super().dies()

