import unittest
from Legum.Pieces.Queen import Queen


class TestQueen(unittest.TestCase):

    def test_queen_instantiated(self):
        queen = Queen(0, (0, 0))
        self.assertEqual(queen.name, "Queen")
        self.assertEqual(queen.color, 0)
        self.assertEqual(queen.position, (0, 0))
        self.assertEqual(queen.is_alive, True)
        
    def test_queen_str(self):
        queen = Queen(0, (0, 0))
        self.assertEqual(str(queen), "Queen 0")

    def test_queen_repr(self):
        queen = Queen(0, (0, 0))
        self.assertEqual(repr(queen), "<Queen 0 (0, 0) True False>")

    def test_queen_call(self):
        queen = Queen(0, (0, 0))
        self.assertEqual(queen(), queen.get_moves_from_direction_vectors())

    def test_queen_get_moves(self):
        queen = Queen(0, (0, 0))
        self.assertEqual(queen.get_moves_from_absolute_vectors(), [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)])

    def test_queen_get_moves_2(self):
        queen = Queen(0, (7, 7))
        self.assertEqual(queen.get_moves_from_absolute_vectors(), [(6, 6), (6, 7), (7, 6)])

    def test_queen_get_moves_3(self):
        queen = Queen(0, (7, 0))
        self.assertEqual(queen.get_moves_from_absolute_vectors(), [(6, 0), (6, 1), (7, 1)])

    def test_queen_get_moves_4(self):
        queen = Queen(0, (0, 7))
        self.assertEqual(queen.get_moves_from_absolute_vectors(), [(0, 6), (1, 6), (1, 7)])

    def test_queen_get_moves_5(self):
        queen = Queen(0, (3, 3))
        self.assertEqual(queen.get_moves_from_absolute_vectors(), [(2, 2), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 3), (4, 4)])

    def test_queen_move(self):
        queen = Queen(0, (3, 3))
        queen.move((4, 4))
        self.assertEqual(queen.position, (4, 4))
        self.assertEqual(queen.is_alive, True)

    def test_queen_dies(self):
        queen = Queen(0, (3, 3))
        queen.dies()
        self.assertEqual(queen.is_alive, False)
