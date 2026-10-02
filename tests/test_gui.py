import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame = pytest.importorskip("pygame")

from legum.components import Board, King  # noqa: E402
from legum.gui import ChessGUI  # noqa: E402


def test_gui_loads_sprites_and_draws_a_board():
    gui = ChessGUI(square_size=40)
    assert len(gui.piece_images) == 12
    board = Board()
    board.place(King("white"), (7, 4))
    gui.draw_board()
    gui.draw_pieces(board)
    assert gui.get_square_from_mouse((45, 85)) == (2, 1)
    pygame.quit()
