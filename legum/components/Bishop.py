from .Piece import Piece


class Bishop(Piece):
    """A class to represent a Bishop chess piece: slides along diagonals."""

    name = "Bishop"
    short_name = "B"
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    sliding = True
    value = 330
