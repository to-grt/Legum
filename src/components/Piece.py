from typing import Tuple

from src.components import Board


class Piece:
    """
    A class to represent a generic chess piece.
    Attributes:
        name (str): The name of the piece (e.g., 'Pawn', 'Rook').
        short_name (str): The abbreviated name of the piece (e.g., 'P', 'R').
        color (str): The color of the piece ('white' or 'black').
        position (Tuple): The current position of the piece on the board as (row, column).
        is_alive (bool): Status indicating if the piece is still in play.
        move_counter (int): Counts the number of moves made by the piece.
    Methods:
        find_moves(board): Abstract method to find valid moves for the piece.
        change_name(new_name): Sets a new name for the piece.
        change_color(new_color): Sets a new color for the piece.
        change_status(is_alive): Updates the alive status of the piece.
        change_position(new_position, board): Updates the position of the piece on the board.
        coord_tuples_to_str(position): Converts position tuple to standard chess notation.
        print_moves_nicely(moves): Prints possible moves in a readable format.
    """

    dict_conversion_letter = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
    dict_conversion_number = {1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2, 7: 1, 8: 0}
    dict_short_names = {'Pawn': 'P', 'Rook': 'R', 'Knight': 'N', 'Bishop': 'B', 'Queen': 'Q', 'King': 'K'}

    const_undefined_str = "undefined"
    const_undefined_position = (-1, -1)
    const_undefined_bool = None

    def __init__(self,
                 board: Board,
                 name: str,
                 color: str,
                 position: Tuple,
                 is_alive: bool,) -> None:

        self.name: str = self.const_undefined_str
        self.change_name(name)
        self.short_name: str = self.dict_short_names.get(name, 'X')

        self.color: str = self.const_undefined_str
        self.change_color(color)

        self.position: Tuple = self.const_undefined_position
        self.change_position(position, board)

        self.is_alive: bool = self.const_undefined_bool
        self.change_status(is_alive)

        self.move_counter: int = 0

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Methods to be overridden by subclasses ------------------------------------------------------------ #
    # --------------------------------------------------------------------------------------------------------------- #
    def find_moves(self, board: Board) -> list:
        raise NotImplementedError("[ERROR]: This method should be implemented by subclasses.")

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Setter -------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def change_name(self, new_name: str) -> None:
        if new_name not in self.dict_short_names.keys():
            raise ValueError(f"Name '{new_name}' is not a valid piece name. Available names: {list(self.dict_short_names.keys())}.")
        self.name = new_name

    def change_color(self, new_color: str) -> None:
        if new_color not in ['white', 'black']:
            raise ValueError(f"Color '{new_color}' is not valid. Choose 'white' or 'black'.")
        self.color = new_color

    def change_status(self, is_alive: bool) -> None:
        if not isinstance(is_alive, bool):
            raise ValueError(f"Status '{is_alive}' must be a boolean value.")
        self.is_alive = is_alive

    def change_position(self, new_position: Tuple, board: Board) -> None:
        if not board.check_position(new_position):
            raise ValueError(f"Position {new_position} is out of board bounds.")
        self.position = new_position

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Methods below are common for all pieces and do not require overriding ----------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def __call__(self):
        return self

    def __str__(self) -> str:
        coords = self.coord_tuples_to_str(self.position)
        return f"A {self.color} {self.name} at {coords}"

    def __repr__(self) -> str:
        return f"{self}: {self.name}, Color: {self.color}, Position: {self.position}, Alive: {self.is_alive}."

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Helpers ------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def coord_tuples_to_str(self, position: Tuple) -> str:
        letter = list(self.dict_conversion_letter.keys())[list(self.dict_conversion_letter.values()).index(position[1])]
        number = list(self.dict_conversion_number.keys())[list(self.dict_conversion_number.values()).index(position[0])]
        return f"{letter}{number}"

    def print_moves_nicely(self, moves: list) -> None:
        move_strs = [self.coord_tuples_to_str(move) for move in moves]
        print(f"{self} can moves from {self.position} to {", ".join(move_strs)}")