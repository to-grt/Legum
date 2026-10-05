from .Piece import Piece


class Queen(Piece):
    """A class to represent a Queen chess piece: slides along ranks, files and diagonals."""

    name = "Queen"
    short_name = "Q"
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    sliding = True
    value = 900
