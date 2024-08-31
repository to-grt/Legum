import unittest
from Legum.Pieces.King import King


class TestKing(unittest.TestCase):

    def test_king_instantiated(self):
        king = King(0, (0, 0))
        self.assertEqual(king.name, "King")
        self.assertEqual(king.color, 0)
        self.assertEqual(king.position, (0, 0))
        self.assertEqual(king.is_alive, True)

    def test_king_str(self):
        king = King(0, (0, 0))
        self.assertEqual(str(king), "King 0")

    def test_king_repr(self):
        king = King(0, (0, 0))
        self.assertEqual(repr(king), "<King 0 (0, 0) True False>")

    def test_king_call(self):
        king = King(0, (0, 0))
        self.assertEqual(king(), king.get_moves_from_direction_vectors())

    def test_king_get_moves(self):
        king = King(0, (0, 0))
        self.assertEqual(king.get_moves_from_absolute_vectors(), [(0, 1), (1, 0), (1, 1)])

    def test_king_get_moves_2(self):
        king = King(0, (7, 7))
        self.assertEqual(king.get_moves_from_absolute_vectors(), [(6, 6), (6, 7), (7, 6)])

    def test_king_get_moves_3(self):
        king = King(0, (7, 0))
        self.assertEqual(king.get_moves_from_absolute_vectors(), [(6, 0), (6, 1), (7, 1)])

    def test_king_get_moves_4(self):
        king = King(0, (0, 7))
        self.assertEqual(king.get_moves_from_absolute_vectors(), [(0, 6), (1, 6), (1, 7)])

    def test_king_get_moves_5(self):
        king = King(0, (3, 3))
        self.assertEqual(king.get_moves_from_absolute_vectors(), [(2, 2), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 3), (4, 4)])

    def test_king_move(self):
        king = King(0, (3, 3))
        king.move((4, 4))
        self.assertEqual(king.position, (4, 4))
        self.assertEqual(king.is_alive, True)

    def test_king_dies(self):
        king = King(0, (3, 3))
        king.dies()
        self.assertEqual(king.is_alive, False)
