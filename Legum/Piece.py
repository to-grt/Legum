# Piece.py

# Imports
from abc import ABC, abstractmethod


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

    def move(self, position: tuple) -> None:
        """
        Move the piece to the given position.
        """
        self.position = position

    def get_moves_from_absolute_vectors(self) -> list:
        """
        Get the possible moves of a piece from the absolute vectors. i.e. the knights, the kings, the pawns.
        Should be implemented in some subclass.
        """
        pass

    def get_moves_from_direction_vectors(self) -> list:
        """
        Get the possible moves of a piece from the direction vectors. i.e. the rooks, the bishops, the queens.
        Should be implemented in some subclass.

        """
        raise Exception("get_moves_from_direction_vectors should be implemented in the subclass.")

    def dies(self) -> None:
        """
        Set the piece as dead.
        """
        self.is_alive = False
        self.position = None