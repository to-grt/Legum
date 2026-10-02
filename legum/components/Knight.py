from .Piece import Piece


class Knight(Piece):
    """A class to represent a Knight chess piece: jumps in an L shape."""

    name = "Knight"
    short_name = "N"
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    value = 320
