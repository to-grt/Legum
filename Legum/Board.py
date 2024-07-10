# Board.py

# Imports
import numpy as np


class Board:

    EMPTY = 0

    WHITE_PAWN = 1
    WHITE_KNIGHT = 2
    WHITE_BISHOP = 3
    WHITE_ROOK = 4
    WHITE_QUEEN = 5
    WHITE_KING = 6

    BLACK_PAWN = 7
    BLACK_KNIGHT = 8
    BLACK_BISHOP = 9
    BLACK_ROOK = 10
    BLACK_QUEEN = 11
    BLACK_KING = 12

    def __init__(self):
        self.board = np.zeros(shape=(8, 8), dtype=int)

    def set_to_defaultr(self):
        self.board = np.array([
            [Board.BLACK_ROOK, Board.BLACK_KNIGHT, Board.BLACK_BISHOP, Board.BLACK_QUEEN, Board.BLACK_KING, Board.BLACK_BISHOP, Board.BLACK_KNIGHT, Board.BLACK_ROOK],
            [Board.BLACK_PAWN, Board.BLACK_PAWN, Board.BLACK_PAWN, Board.BLACK_PAWN, Board.BLACK_PAWN, Board.BLACK_PAWN, Board.BLACK_PAWN, Board.BLACK_PAWN],
            [Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY],
            [Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY],
            [Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY],
            [Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY, Board.EMPTY],
            [Board.WHITE_PAWN, Board.WHITE_PAWN, Board.WHITE_PAWN, Board.WHITE_PAWN, Board.WHITE_PAWN, Board.WHITE_PAWN, Board.WHITE_PAWN, Board.WHITE_PAWN],
            [Board.WHITE_ROOK, Board.WHITE_KNIGHT, Board.WHITE_BISHOP, Board.WHITE_QUEEN, Board.WHITE_KING, Board.WHITE_BISHOP, Board.WHITE_KNIGHT, Board.WHITE_ROOK]
        ])


