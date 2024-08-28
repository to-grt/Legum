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
        self.moves = None

    def __repr__(self) -> str:
        return f"<Piece>"

    def __str__(self) -> str:
        return f"Piece"
