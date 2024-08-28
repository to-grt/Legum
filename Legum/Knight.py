# Knight.py


# Imports
from Legum.Piece import Piece


class Knight(Piece):

    def __init__(self, color: int, position: tuple) -> None:
        super().__init__()
        self.name = "Knight"
        self.color = color
        self.position = position


    def __repr__(self) -> str:
        return f"<Knight {self.color} {self.position}>"

    def __str__(self) -> str:
        return f"Knight {self.color}"

    def __call__(self) -> str:
        return self.__str__()

    @staticmethod
    def get_vectors() -> list:
        """
        Get the vectors of the possible moves of the knight on the board.
        """
        return [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    def get_moves(self) -> list:
        """
        Get the destination squares of the knight on the board. Color is not taken into account because
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


