# Piece.py

# Imports
from abc import ABC


class Piece(ABC):
    """
    Class representing a piece of the piece, should not be instanced, instead use the subclasses.
    """

    def __init__(self) -> None:
        if type(self) == Piece:
            raise Exception("<Piece> should not be instantiated, use the subclasses")
        self.name = None
        self.color = None
        self.position = None
        self.is_alive = None

    def __repr__(self) -> str:
        return f"<Piece>"

    def __str__(self) -> str:
        return f"Piece"

    def get_vectors(self) -> list:
        """
        Get the vectors of the possible moves of the piece on the board.
        This will be as direction vectors, or as absolute vectors, depending on the piece.
        """
        pass

    def move(self, position: tuple) -> None:
        self.position = position

    def get_moves_from_vectors(self, vectors: list) -> list:
        """
        Get the destination squares of the piece on the board. Color is not taken into account because
        the moves are the same independently of the color of the piece.
        """
        moves = []
        for vector in vectors:
            move = (self.position[0] + vector[0], self.position[1] + vector[1])
            if 0 <= move[0] < 8 and 0 <= move[1] < 8:
                moves.append(move)
        return moves

    def get_moves_from_directions(self, directions: list) -> list:
        """
        Get the destination squares of the piece on the board.
        """
        # TODO: do it :)
        return []

    def dies(self) -> None:
        """
        Set the piece as dead.
        """
        self.is_alive = False
        self.position = None