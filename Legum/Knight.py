# Knight.py


# Imports
from Legum.Piece import Piece


class Knight(Piece):

    def __init__(self, color: int, position: tuple) -> None:
        super().__init__()
        self.name = "Knight"
        self.color = color
        self.position = position
        self.is_alive = True


    def __repr__(self) -> str:
        return f"<Knight {self.color} {self.position} {self.is_alive}>"

    def __str__(self) -> str:
        return f"Knight {self.color}"

    def __call__(self) -> list:
        """
        Get the moves of the knight on the board.
        :return:
        """
        return self.get_moves()

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
        """
        vectors = self.get_vectors()
        return self.get_moves_from_vectors(vectors)

    def get_moves_from_vectors(self, vectors: list) -> list:
        """
        Get the destination squares of the knight on the board. Color is not taken into account because
        the moves are the same independently of the color of the piece.
        TODO: will be updated to take into account the whole board, and especially the other pieces.
        """
        return super().get_moves_from_vectors(vectors)

    def get_moves_from_directions(self, vectors: list) -> list:
        """
        Should not be used for the knight.
        """
        raise Exception("Knight does not have directions, use get_moves_from_vectors instead.")

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
