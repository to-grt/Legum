import unittest
from Legum.Knight import Knight

class TestKnight(unittest.TestCase):

    def test_knight_instantiated(self):
        knight = Knight(0, (0, 0))
        self.assertEqual(knight.name, "Knight")
        self.assertEqual(knight.color, 0)
        self.assertEqual(knight.position, (0, 0))

    def test_knight_str(self):
        knight = Knight(0, (0, 0))
        self.assertEqual(str(knight), "Knight 0")

    def test_knight_repr(self):
        knight = Knight(0, (0, 0))
        self.assertEqual(repr(knight), "<Knight 0 (0, 0)>")

    def test_knight_call(self):
        knight = Knight(0, (0, 0))
        self.assertEqual(str(knight), "Knight 0")

    def test_knight_get_vectors(self):
        knight = Knight(0, (0, 0))
        self.assertEqual(knight.get_vectors(), [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)])

    def test_knight_get_moves(self):
        knight = Knight(0, (0, 0))
        self.assertEqual(knight.get_moves(), [(1, 2), (2, 1)])

    def test_knight_get_moves_2(self):
        knight = Knight(0, (7, 7))
        self.assertEqual(knight.get_moves(), [(5, 6), (6, 5)])

    def test_knight_get_moves_3(self):
        knight = Knight(0, (7, 0))
        self.assertEqual(knight.get_moves(), [(5, 1), (6, 2)])

    def test_knight_get_moves_4(self):
        knight = Knight(0, (0, 7))
        self.assertEqual(knight.get_moves(), [(1, 5), (2, 6)])

    def test_knight_get_moves_5(self):
        knight = Knight(0, (3, 3))
        self.assertEqual(knight.get_moves(), [(1, 2), (1, 4), (2, 1), (2, 5), (4, 1), (4, 5), (5, 2), (5, 4)])
