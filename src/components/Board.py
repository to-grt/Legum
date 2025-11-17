import numpy as np

from src.components import Piece


class Board:
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