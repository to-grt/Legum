import pytest

from legum.components import Board, Color, King, coord_to_str, str_to_coord


def test_color_parsing_and_opposite():
    assert Color("white") is Color.WHITE
    assert Color.WHITE.opposite is Color.BLACK
    with pytest.raises(ValueError):
        King("red")


@pytest.mark.parametrize("position, name", [((7, 0), "A1"), ((0, 7), "H8"), ((4, 4), "E4")])
def test_coordinates_round_trip(position, name):
    assert coord_to_str(position) == name
    assert str_to_coord(name.lower()) == position


def test_check_position():
    board = Board()
    assert board.check_position((0, 0)) and board.check_position((7, 7))
    assert not board.check_position((-1, 0)) and not board.check_position((0, 8))


def test_place_remove_keeps_position_in_sync():
    board = Board()
    king = King("white")
    board.place(king, (4, 4))
    assert board[4, 4] is king and king.position == (4, 4)
    with pytest.raises(ValueError):
        board.place(King("black"), (4, 4))
    with pytest.raises(ValueError):
        board.place(King("black"), (8, 0))
    assert board.remove((4, 4)) is king
    assert board[4, 4] is None and king.position is None


def test_move_piece_returns_capture():
    board = Board()
    white, black = King("white"), King("black")
    board.place(white, (4, 4))
    board.place(black, (3, 4))
    assert board.move_piece((4, 4), (3, 4)) is black
    assert white.position == (3, 4) and black.position is None


def test_board_str_with_pieces():
    # Used to raise because `Piece` was bound to the module instead of the class (circular import)
    board = Board()
    board.place(King("white"), (7, 4))
    board.place(King("black"), (0, 4))
    text = str(board)
    assert text.splitlines()[0] == "8 |   |   |   |   | k |   |   |   |"
    assert text.splitlines()[7] == "1 |   |   |   |   | K |   |   |   |"


def test_sprite_key():
    assert King("black").sprite_key == "b_K"


@pytest.mark.parametrize("position, expected", [
    ((4, 4), 8),   # centre
    ((7, 0), 3),   # corner
    ((7, 4), 5),   # edge
])
def test_king_moves_on_empty_board(position, expected):
    board = Board()
    king = King("white")
    board.place(king, position)
    assert len(king.find_moves(board)) == expected


def test_king_cannot_take_own_piece_but_can_take_opponent():
    board = Board()
    king = King("white")
    board.place(king, (4, 4))
    board.place(King("white"), (3, 4))
    board.place(King("black"), (5, 4))
    moves = king.find_moves(board)
    assert (3, 4) not in moves and (5, 4) in moves
