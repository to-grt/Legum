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
        directions (List[Tuple]): (d_row, d_col) steps the piece moves along, defined by each subclass.
        sliding (bool): True if the piece repeats its steps until blocked (Rook, Bishop, Queen).
        value (int): Material value in centipawns, used by the engine.
    Methods:
        find_moves(board): Returns the squares the piece can reach (empty or occupied by an opponent),
                           without checking whether its own king is left in check.
        sprite_key: Name of the image used by the GUI (e.g., 'w_K').
        print_moves_nicely(moves): Prints possible moves in a readable format.
    """

    name = "Piece"
    short_name = "X"
    directions: List[Tuple[int, int]] = []
    sliding = False
    value = 0

    def __init__(self, color: Color | str) -> None:
        self.color: Color = Color(color)
        self.position: Optional[Tuple[int, int]] = None

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Can be overridden by subclasses (the Pawn does) --------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def find_moves(self, board: Board) -> List[Tuple[int, int]]:
        if self.position is None:
            raise ValueError(f"{self!r} is not on the board.")
        possible_moves = []
        row, col = self.position
        for d_row, d_col in self.directions:
            target = (row + d_row, col + d_col)
            while board.check_position(target):
                target_cell = board[target]
                if target_cell is None:
                    possible_moves.append(target)
                elif target_cell.color != self.color:
                    possible_moves.append(target)
                    break
                else:
                    break
                if not self.sliding:
                    break
                target = (target[0] + d_row, target[1] + d_col)
        return possible_moves

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
