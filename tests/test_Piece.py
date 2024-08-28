import unittest
from Legum.Piece import Piece


class TestPiece(unittest.TestCase):

    def test_piece_not_instantiated(self):
        with self.assertRaises(Exception):
            Piece()
