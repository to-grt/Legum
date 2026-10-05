from .Piece import Piece


class Rook(Piece):
    """A class to represent a Rook chess piece: slides along ranks and files."""

    name = "Rook"
    short_name = "R"
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    sliding = True
    value = 500
