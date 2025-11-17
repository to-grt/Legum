from typing import Tuple

from src.components import Board


class Piece:
    """
    A class to represent a generic chess piece.
    Attributes:
        name (str): The name of the piece.
        color (str): The color of the piece ('white' or 'black').
        position (Tuple): The current position of the piece on the board (row, column).
        is_alive (bool): Status indicating if the piece is still in play.
    Methods:
        change_name(new_name): Updates the piece's name.
        change_color(new_color): Updates the piece's color.
        move(new_position): Updates the piece's position.
        vanish(): Sets the piece's status to not alive.
        resurrect(): Sets the piece's status to alive.
        check_position(position): Validates if the position is within the board limits.
        __call__(): Returns the piece instance.
        __str__(): Returns a string representation of the piece.
        __repr__(): Returns a detailed string representation of the piece.
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
    def find_moves(self, board) -> list:
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
        letter = list(self.dict_conversion_letter.keys())[list(self.dict_conversion_letter.values()).index(self.position[1])]
        number = list(self.dict_conversion_number.keys())[list(self.dict_conversion_number.values()).index(self.position[0])]
        return f"A {self.color} {self.name} at {letter}{number}"

    def __repr__(self) -> str:
        return f"{self}: {self.name}, Color: {self.color}, Position: {self.position}, Alive: {self.is_alive}."