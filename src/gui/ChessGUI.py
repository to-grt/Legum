import pygame

from typing import Tuple

from const_paths import path_pieces


class ChessGUI:
    """
    A simple chess GUI using Pygame.
    Attributes:
        square_size (int): Size of each square on the chess board.
        board_size (int): Number of squares along one side of the board (default is 8).
        screen (pygame.Surface): The main display surface.
    Methods:
        draw_board(): Draws the chess board.
        draw_pieces(board_state): Draws the pieces on the board based on the given state.
        get_square_from_mouse(pos): Converts mouse position to board coordinates.
        highlight_square(row, col): Highlights a specific square on the board.
        run(board_state): Main loop to run the GUI.
    """
    def __init__(self, square_size: int = 80, board_size: int = 8):
        pygame.init()
        self.square_size = square_size
        self.board_size = board_size
        self.width = self.height = self.square_size * self.board_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess")

        # Load your piece images
        self.piece_images = {}
        # Example: self.piece_images['wp'] = pygame.image.load('white_pawn.png')

        # Colors (light/dark squares)
        self.light_square = (240, 217, 181)
        self.dark_square = (181, 136, 99)
        # Alternative green: (238, 238, 210) and (118, 150, 86)

        self.selected_square = None

    def load_pieces_resources(self):
        pieces = ['w_P', 'w_R', 'w_N', 'w_B', 'w_Q', 'w_K',
                  'b_P', 'b_R', 'b_N', 'b_B', 'b_Q', 'b_K']
        for piece in pieces:
            path = path_pieces / f"{piece}.png"
            self.piece_images[piece] = pygame.image.load(str(path))
            self.piece_images[piece] = pygame.transform.scale(
                self.piece_images[piece],
                (self.square_size, self.square_size)
            )

    def draw_board(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = self.light_square if (row + col) % 2 == 0 else self.dark_square
                rect = pygame.Rect(col * self.square_size, row * self.square_size,
                                   self.square_size, self.square_size)
                pygame.draw.rect(self.screen, color, rect)

    def draw_pieces(self, board):
        """
        board_state: board representation (e.g., 'w_P' for white pawn, None for empty)
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = board[row][col]
                if piece and piece in self.piece_images:
                    img = self.piece_images[piece]
                    x = col * self.square_size
                    y = row * self.square_size
                    self.screen.blit(img, (x, y))

    def get_square_from_mouse(self, pos: Tuple) ->  Tuple[int, int]:
        """Convert pixel position to (row, col)"""
        x, y = pos
        return y // self.square_size, x // self.square_size

    def highlight_square(self, row: int, col: int):
        """Highlight selected square"""
        overlay = pygame.Surface((self.square_size, self.square_size))
        overlay.set_alpha(100)
        overlay.fill((255, 255, 0))
        self.screen.blit(overlay, (col * self.square_size, row * self.square_size))

    def run(self, board):
        """
        Main loop to run the chess GUI.
        board: representation of the board
        """
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = self.get_square_from_mouse(pos)
                    # YOUR LOGIC HERE
                    print(f"Clicked: {row}, {col}")
                    self.selected_square = (row, col)

            self.draw_board()
            if self.selected_square:
                self.highlight_square(*self.selected_square)
            self.draw_pieces(board)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()