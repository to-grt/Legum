from __future__ import annotations

from typing import Iterator, Optional, Tuple

import numpy as np

from .Bishop import Bishop
from .Color import Color
from .King import King
from .Knight import Knight
from .Pawn import Pawn
from .Piece import Piece
from .Queen import Queen
from .Rook import Rook
from .coords import FILES

PIECE_CLASSES = {cls.short_name: cls for cls in (Pawn, Knight, Bishop, Rook, Queen, King)}
STARTING_PLACEMENT = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


class Board:
    """
    A class to represent a chess board. It is the single source of truth for piece placement.
    Attributes:
        board_size (int): The size of the chess board (default is 8 for an 8x8 board).
        board (np.ndarray): A 2D numpy array of Piece instances, None for empty cells.
    Methods:
        empty_board(): Removes every piece from the board.
        reset_board(): Sets up the standard chess starting position.
        set_placement(placement): Sets up the pieces from the first field of a FEN string.
        placement(): Returns the first field of the FEN string describing the board.
        check_position(position): Checks if a given position is within the bounds of the board.
        place(piece, position): Puts a piece on an empty square.
        remove(position): Removes and returns the piece on a square.
        move_piece(start, end): Moves a piece, returning the captured piece if any.
        pieces(color): Iterates over the pieces on the board.
    """

    def __init__(self, board_size: int = 8) -> None:
        self.board_size: int = board_size
        self.board = np.full((board_size, board_size), None, dtype=object)

    def empty_board(self) -> None:
        for piece in list(self.pieces()):
            piece.position = None
        self.board = np.full((self.board_size, self.board_size), None, dtype=object)

    def reset_board(self) -> None:
        if self.board_size != 8:
            raise NotImplementedError("Resetting board is only implemented for standard 8x8 chess board.")
        self.set_placement(STARTING_PLACEMENT)

    def set_placement(self, placement: str) -> None:
        """
        Sets up the board from the piece placement field of a FEN string,
        e.g. 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'. Uppercase is white, lowercase is black.
        """
        rows = placement.split("/")
        if len(rows) != self.board_size:
            raise ValueError(f"Placement '{placement}' must have {self.board_size} rows.")
        self.empty_board()
        for row, row_str in enumerate(rows):
            col = 0
            for char in row_str:
                if char.isdigit():
                    col += int(char)
                    continue
                piece_class = PIECE_CLASSES.get(char.upper())
                if piece_class is None:
                    raise ValueError(f"Unknown piece '{char}' in placement '{placement}'.")
                color = Color.WHITE if char.isupper() else Color.BLACK
                self.place(piece_class(color), (row, col))
                col += 1
            if col != self.board_size:
                raise ValueError(f"Row '{row_str}' of placement '{placement}' does not have {self.board_size} squares.")

    def placement(self) -> str:
        rows = []
        for row in self.board:
            row_str, empty = "", 0
            for cell in row:
                if cell is None:
                    empty += 1
                    continue
                if empty:
                    row_str += str(empty)
                    empty = 0
                row_str += cell.short_name if cell.color is Color.WHITE else cell.short_name.lower()
            if empty:
                row_str += str(empty)
            rows.append(row_str)
        return "/".join(rows)

    def check_position(self, position: Tuple[int, int]) -> bool:
        row, col = position
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def __getitem__(self, position: Tuple[int, int]) -> Optional[Piece]:
        return self.board[position]

    def place(self, piece: Piece, position: Tuple[int, int]) -> None:
        if not self.check_position(position):
            raise ValueError(f"Position {position} is out of board bounds.")
        if self.board[position] is not None:
            raise ValueError(f"Position {position} is already occupied by {self.board[position]}.")
        self.board[position] = piece
        piece.position = position

    def remove(self, position: Tuple[int, int]) -> Optional[Piece]:
        piece = self.board[position]
        if piece is not None:
            self.board[position] = None
            piece.position = None
        return piece

    def move_piece(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[Piece]:
        piece = self.remove(start)
        if piece is None:
            raise ValueError(f"No piece at {start}.")
        captured = self.remove(end)
        self.place(piece, end)
        return captured

    def pieces(self, color: Optional[Color] = None) -> Iterator[Piece]:
        for piece in self.board.flat:
            if piece is not None and (color is None or piece.color == color):
                yield piece

    def __str__(self) -> str:
        lines = []
        for row_index, row in enumerate(self.board):
            cells = []
            for cell in row:
                if cell is None:
                    cells.append(" ")
                elif isinstance(cell, Piece):
                    # Uppercase for white, lowercase for black, as in FEN
                    cells.append(cell.short_name if cell.color is Color.WHITE else cell.short_name.lower())
                else:
                    raise TypeError("Board can only contain Piece instances or None for empty cells.")
            lines.append(f"{self.board_size - row_index} | " + " | ".join(cells) + " |")
        lines.append("    " + "   ".join(FILES[:self.board_size]))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Board(size={self.board_size})"
