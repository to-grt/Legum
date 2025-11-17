import numpy as np

from src.components import Piece


class Board:
    """
    A class to represent a chess board.
    Attributes:
        board_size (int): The size of the chess board (default is 8 for an 8x8 board).
        board (np.ndarray): A 2D numpy array representing the chess board.
    Methods:
        empty_board(): Empties the board by setting all positions to 0.
        reset_board(): Resets the board to the standard chess starting position.
        check_position(position): Checks if a given position is within the bounds of the board.
        __str__(): Returns a string representation of the board.
        __repr__(): Returns a formal string representation of the Board object.
    """
    def __init__(self, board_size: int = 8) -> None:
        self.board_size: int = board_size
        self.board = np.zeros((board_size, board_size), dtype=object)

    def empty_board(self) -> None:
        self.board = np.zeros((self.board_size, self.board_size), dtype=object)

    def reset_board(self) -> None:
        if self.board_size != 8:
            raise NotImplementedError("Resetting board is only implemented for standard 8x8 chess board.")
        # TODO: Implement standard chess starting position

    def check_position(self, position: tuple) -> bool:
        row, col = position
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def __str__(self) -> str:
         for row in self.board:
            row_str = ' | '
            for cell in row:
                if cell == 0:
                    row_str += '   | '
                elif isinstance(cell, Piece):
                    row_str += f' {cell.short_name} | '
                else:
                    raise TypeError("Board can only contain Piece instances or 0 for empty cells.")
            print(row_str)
         return ""

    def __repr__(self) -> str:
        return f"Board(size={self.board_size})"