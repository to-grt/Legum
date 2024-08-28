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

    def __call__(self) -> str:
        return self.__str__()

    @staticmethod
    def get_vectors() -> list:
        """
        Get the vectors of the possible moves of the king on the board.
        """
        return [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def get_moves_from_directions(self) -> list:
        """
        Get the destination squares of the king on the board. Color is not taken into account because
        the moves are the same independently of the color of the piece.
        TODO: will be updated to take into account the whole board, and especially the other pieces.
        """
        vectors = self.get_vectors()
        moves = []
        for vector in vectors:
            move = (self.position[0] + vector[0], self.position[1] + vector[1])
            if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                moves.append(move)
        return moves

    def move(self, position: tuple) -> None:
        """
        Move the king to the given position.
        """
        super().move(position)

    def dies(self) -> None:
        """
        Set the piece as dead.
        """
        super().dies()