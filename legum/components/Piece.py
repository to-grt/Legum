from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from .Color import Color
from .coords import coord_to_str

if TYPE_CHECKING:
    from .Board import Board


class Piece:
    """
    A class to represent a generic chess piece.
    The board is the source of truth for where pieces are: `position` is kept up to date by Board.place/remove.
    Attributes:
        name (str): The name of the piece (e.g., 'Pawn', 'Rook'), defined by each subclass.
        short_name (str): The abbreviated name of the piece (e.g., 'P', 'R'), defined by each subclass.
        color (Color): The color of the piece.
        position (Tuple | None): The current position of the piece as (row, column), None when off the board.
    Methods:
        find_moves(board): Abstract method to find the target squares of the piece.
        sprite_key: Name of the image used by the GUI (e.g., 'w_K').
        print_moves_nicely(moves): Prints possible moves in a readable format.
    """

    name = "Piece"
    short_name = "X"

    def __init__(self, color: Color | str) -> None:
        self.color: Color = Color(color)
        self.position: Optional[Tuple[int, int]] = None

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Methods to be overridden by subclasses ------------------------------------------------------------ #
    # --------------------------------------------------------------------------------------------------------------- #
    def find_moves(self, board: Board) -> List[Tuple[int, int]]:
        raise NotImplementedError("[ERROR]: This method should be implemented by subclasses.")

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Methods below are common for all pieces and do not require overriding ----------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    @property
    def sprite_key(self) -> str:
        return f"{self.color.prefix}_{self.short_name}"

    def __str__(self) -> str:
        where = coord_to_str(self.position) if self.position is not None else "nowhere"
        return f"A {self.color.value} {self.name} at {where}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(color={self.color.value!r}, position={self.position})"

    def print_moves_nicely(self, moves: List[Tuple[int, int]]) -> None:
        move_strs = [coord_to_str(move) for move in moves]
        print(f"{self} can move to {', '.join(move_strs)}")
