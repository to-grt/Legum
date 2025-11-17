from src.components.Piece import Piece


class King(Piece):
    """
    A class to represent a King chess piece, inheriting from the Piece class.
    Attributes:
        Inherits all attributes from Piece.
    Methods:
        find_moves(board): Returns a list of valid moves for the King piece.
    """

    def __init__(self,
                 color: str,
                 position: tuple = (-1, -1),
                 is_alive: bool = True) -> None:
        if color not in ['white', 'black']:
            raise ValueError("Color must be 'white' or 'black'.")
        super().__init__(name="King", color=color, position=position, is_alive=is_alive)

    def find_moves(self, board) -> list:
        possible_moves = []
        row, col = self.position
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if board.check_position((new_row, new_col)):
                target_cell = board.board[new_row][new_col]
                if target_cell == 0 or target_cell.color != self.color:
                    possible_moves.append((new_row, new_col))
        return possible_moves