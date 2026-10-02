import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame = pytest.importorskip("pygame")

from legum.components import Color, Queen  # noqa: E402
from legum.gui import ChessGUI  # noqa: E402
from legum.game import GameState, Move  # noqa: E402


@pytest.fixture
def gui():
    gui = ChessGUI(square_size=40)
    yield gui
    pygame.quit()


def click(gui, square):
    row, col = square
    gui.handle_click((col * gui.square_size + 5, row * gui.square_size + 5))


def test_gui_loads_sprites_and_renders(gui):
    assert len(gui.piece_images) == 12
    gui.render()
    assert gui.get_square_from_mouse((45, 85)) == (2, 1)
    assert gui.get_square_from_mouse((10, gui.width + 5)) is None  # Status bar


def test_select_and_move(gui):
    click(gui, (6, 4))  # e2
    assert gui.selected_square == (6, 4)
    assert {move.uci for move in gui.selected_moves} == {"e2e3", "e2e4"}
    click(gui, (4, 4))  # e4
    assert gui.state.turn is Color.BLACK and gui.last_move.uci == "e2e4"
    gui.render()


def test_cannot_select_opponent_piece(gui):
    click(gui, (1, 4))  # Black pawn while white is to move
    assert gui.selected_square is None


def test_promotion_choice():
    gui = ChessGUI(GameState("8/P6k/8/8/8/8/8/K7 w - - 0 1"), square_size=40)
    click(gui, (1, 0))
    click(gui, (0, 0))
    assert len(gui.pending_promotion) == 4
    gui.render()
    click(gui, (1, 0))  # Choices are drawn downwards from a8: Q, R, B, N
    assert gui.state.board[0, 0].short_name == "R"
    gui.undo()
    click(gui, (1, 0))
    click(gui, (0, 0))
    click(gui, (0, 0))
    assert isinstance(gui.state.board[0, 0], Queen)
    pygame.quit()


def test_engine_answers_and_undo_goes_back_to_human(gui):
    gui.ai_color, gui.ai_depth = Color.BLACK, 1
    click(gui, (6, 4))
    click(gui, (4, 4))
    gui.update_ai()  # Starts the engine thread
    gui._ai_thread.join(timeout=30)
    gui.update_ai()  # Plays its move
    assert gui.state.turn is Color.WHITE and len(gui.state.history) == 2
    gui.undo()
    assert gui.state.turn is Color.WHITE and not gui.state.history


def test_game_over_status(gui):
    for move in ["f2f3", "e7e5", "g2g4", "d8h4"]:
        gui.play(Move.from_uci(move))
    assert gui.outcome.reason == "checkmate"
    assert gui.status_text().startswith("0-1")
    assert not gui.human_to_move
