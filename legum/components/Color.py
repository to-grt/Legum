from enum import Enum


class Color(Enum):
    """
    The two sides of a chess game.
    Values are the lowercase names, so Color("white") is Color.WHITE.
    """
    WHITE = "white"
    BLACK = "black"

    @property
    def opposite(self) -> "Color":
        return Color.BLACK if self is Color.WHITE else Color.WHITE

    @property
    def prefix(self) -> str:
        """Single letter used in sprite names and FEN ('w' or 'b')."""
        return self.value[0]
