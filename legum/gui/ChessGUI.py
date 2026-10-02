import threading
from typing import List, Optional, Tuple

import pygame

from legum.components import Color
from legum.const_paths import path_pieces
from legum.engine import find_best_move
from legum.game import GameState, Move
from legum.game.GameState import PROMOTION_CHOICES


class ChessGUI:
    """
    A chess GUI using Pygame. Human vs human, or human vs the engine.
    Controls: click a piece then a target square; N = new game, U = undo, Esc = quit.
    Attributes:
        state (GameState): The game being played. The GUI only uses its public API.
        ai_color (Color | None): Side played by the engine, None for two human players.
        ai_depth (int): Search depth of the engine.
    Methods:
        handle_click(pos): Reacts to a mouse click (selection, move, promotion choice).
        new_game() / undo(): Restart / take back the last move (two moves against the engine).
        render(): Draws the whole window.
        run(): Main loop.
    """
    status_height = 32

    def __init__(self, state: Optional[GameState] = None, ai_color: Optional[Color] = None, ai_depth: int = 3,
                 ai_time_limit: Optional[float] = 10.0, square_size: int = 80):
        pygame.display.init()  # Not pygame.init(): no need for sound
        pygame.font.init()
        self.state = state or GameState()
        self.start_fen = self.state.fen()
        self.ai_color = ai_color
        self.ai_depth = ai_depth
        self.ai_time_limit = ai_time_limit

        self.square_size = square_size
        self.board_size = self.state.board.board_size
        self.width = self.square_size * self.board_size
        self.height = self.width + self.status_height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Legum")
        self.font = pygame.font.Font(None, 26)

        self.piece_images = {}
        self.load_pieces_resources()

        # Colors (light/dark squares)
        self.light_square = (240, 217, 181)
        self.dark_square = (181, 136, 99)
        # Alternative green: (238, 238, 210) and (118, 150, 86)

        self.selected_square: Optional[Tuple[int, int]] = None
        self.selected_moves: List[Move] = []
        self.pending_promotion: List[Move] = []  # The 4 promotion moves while the player chooses a piece
        self.last_move: Optional[Move] = None
        self.outcome = self.state.outcome()

        self._ai_thread: Optional[threading.Thread] = None
        self._ai_move: Optional[Move] = None

    def load_pieces_resources(self):
        pieces = ['w_P', 'w_R', 'w_N', 'w_B', 'w_Q', 'w_K',
                  'b_P', 'b_R', 'b_N', 'b_B', 'b_Q', 'b_K']
        for piece in pieces:
            path = path_pieces / f"{piece}.png"
            image = pygame.image.load(str(path))
            self.piece_images[piece] = pygame.transform.smoothscale(image, (self.square_size, self.square_size))

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Game logic ---------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    @property
    def ai_thinking(self) -> bool:
        return self._ai_thread is not None

    @property
    def human_to_move(self) -> bool:
        return self.outcome is None and not self.ai_thinking and self.state.turn != self.ai_color

    def get_square_from_mouse(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert pixel position to (row, col), None outside the board"""
        x, y = pos
        if not (0 <= x < self.width and 0 <= y < self.width):
            return None
        return y // self.square_size, x // self.square_size

    def promotion_squares(self) -> List[Tuple[int, int]]:
        """Squares where the promotion choices are drawn: from the target square towards the centre."""
        end = self.pending_promotion[0].end
        step = 1 if end[0] == 0 else -1
        return [(end[0] + i * step, end[1]) for i in range(len(PROMOTION_CHOICES))]

    def handle_click(self, pos: Tuple[int, int]) -> None:
        square = self.get_square_from_mouse(pos)
        if square is None or not self.human_to_move:
            return

        if self.pending_promotion:
            squares = self.promotion_squares()
            if square in squares:
                self.play(self.pending_promotion[squares.index(square)])
            self.pending_promotion = []
            self._clear_selection()
            return

        targets = [move for move in self.selected_moves if move.end == square]
        if targets:
            if len(targets) > 1:  # Promotion: one move per piece choice
                self.pending_promotion = sorted(targets, key=lambda move: PROMOTION_CHOICES.index(move.promotion))
            else:
                self.play(targets[0])
            return

        piece = self.state.board[square]
        if piece is not None and piece.color == self.state.turn and square != self.selected_square:
            self.selected_square = square
            self.selected_moves = [move for move in self.state.legal_moves() if move.start == square]
        else:
            self._clear_selection()

    def _clear_selection(self) -> None:
        self.selected_square = None
        self.selected_moves = []

    def play(self, move: Move) -> None:
        self.state.play(move)
        self.last_move = move
        self._clear_selection()
        self.pending_promotion = []
        self.outcome = self.state.outcome()

    def new_game(self) -> None:
        if self.ai_thinking:
            return
        self.state.set_fen(self.start_fen)
        self.last_move = None
        self._clear_selection()
        self.pending_promotion = []
        self.outcome = self.state.outcome()

    def undo(self) -> None:
        if self.ai_thinking or not self.state.history:
            return
        self.state.unmake_move()
        # Against the engine, go back to the human's turn
        if self.state.turn == self.ai_color and self.state.history:
            self.state.unmake_move()
        self.last_move = self.state.history[-1].move if self.state.history else None
        self._clear_selection()
        self.pending_promotion = []
        self.outcome = self.state.outcome()

    def update_ai(self) -> None:
        """Starts the engine in a thread when it is its turn, and plays its move once found."""
        if self._ai_thread is not None:
            if self._ai_thread.is_alive():
                return
            self._ai_thread = None
            if self._ai_move is not None:
                self.play(self._ai_move)
            return
        if self.outcome is None and self.state.turn == self.ai_color:
            # The engine searches a copy, so drawing the board while it thinks is safe
            search_state = GameState(self.state.fen())
            search_state.position_keys = list(self.state.position_keys)

            def think():
                self._ai_move = find_best_move(search_state, self.ai_depth, self.ai_time_limit)

            self._ai_move = None
            self._ai_thread = threading.Thread(target=think, daemon=True)
            self._ai_thread.start()

    def status_text(self) -> str:
        if self.outcome is not None:
            return f"{self.outcome.result} ({self.outcome.reason}) - N: new game, U: undo"
        side = self.state.turn.value.capitalize()
        if self.ai_thinking:
            return f"{side} (engine) is thinking..."
        if self.pending_promotion:
            return "Choose the promotion piece"
        check = " - check!" if self.state.in_check() else ""
        return f"{side} to move{check}"

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Drawing ------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def draw_board(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = self.light_square if (row + col) % 2 == 0 else self.dark_square
                rect = pygame.Rect(col * self.square_size, row * self.square_size,
                                   self.square_size, self.square_size)
                pygame.draw.rect(self.screen, color, rect)

    def draw_pieces(self):
        for piece in self.state.board.pieces():
            row, col = piece.position
            self.screen.blit(self.piece_images[piece.sprite_key], (col * self.square_size, row * self.square_size))

    def highlight_square(self, row: int, col: int, color=(255, 255, 0), alpha: int = 100):
        overlay = pygame.Surface((self.square_size, self.square_size))
        overlay.set_alpha(alpha)
        overlay.fill(color)
        self.screen.blit(overlay, (col * self.square_size, row * self.square_size))

    def draw_move_hints(self):
        for move in self.selected_moves:
            row, col = move.end
            center = (col * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2)
            radius = self.square_size // 2 - 4 if self.state.board[move.end] is not None else self.square_size // 7
            width = 4 if self.state.board[move.end] is not None else 0
            pygame.draw.circle(self.screen, (70, 70, 70), center, radius, width)

    def draw_promotion_choice(self):
        color = self.state.turn
        for square, choice in zip(self.promotion_squares(), PROMOTION_CHOICES):
            row, col = square
            rect = pygame.Rect(col * self.square_size, row * self.square_size, self.square_size, self.square_size)
            pygame.draw.rect(self.screen, (250, 250, 250), rect)
            pygame.draw.rect(self.screen, (60, 60, 60), rect, 2)
            self.screen.blit(self.piece_images[f"{color.prefix}_{choice}"], rect.topleft)

    def draw_status(self):
        rect = pygame.Rect(0, self.width, self.width, self.status_height)
        pygame.draw.rect(self.screen, (40, 40, 40), rect)
        text = self.font.render(self.status_text(), True, (235, 235, 235))
        self.screen.blit(text, (10, self.width + (self.status_height - text.get_height()) // 2))

    def render(self):
        self.draw_board()
        if self.last_move is not None:
            for square in (self.last_move.start, self.last_move.end):
                self.highlight_square(*square, color=(155, 199, 0), alpha=110)
        if self.state.in_check():
            self.highlight_square(*self.state.kings[self.state.turn], color=(220, 30, 30), alpha=140)
        if self.selected_square:
            self.highlight_square(*self.selected_square)
        self.draw_pieces()
        self.draw_move_hints()
        if self.pending_promotion:
            self.draw_promotion_choice()
        self.draw_status()

    def run(self):
        """
        Main loop to run the chess GUI.
        """
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_n:
                        self.new_game()
                    elif event.key == pygame.K_u:
                        self.undo()

            self.update_ai()
            self.render()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
