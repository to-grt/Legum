import unittest
from Legum.Board import Board


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_initialization(self):
        expected_empty_board = [[0 for _ in range(8)] for _ in range(8)]
        self.assertEqual(self.board.board.tolist(), expected_empty_board, "Board should be initialized empty")

    def test_set_to_default(self):
        self.board.set_to_default()
        expected_default_setup = [
            [10, 8, 9, 11, 12, 9, 8, 10],
            [7, 7, 7, 7, 7, 7, 7, 7],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4]
        ]
        self.assertEqual(self.board.board.tolist(), expected_default_setup, "Default board setup is incorrect")
