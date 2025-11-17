from typing import Tuple


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

    def __init__(self,
                 name: str = "Piece",
                 color: str = "undefined",
                 position: Tuple = (-1, -1),
                 is_alive: bool = True) -> None:
        self.name: str = name               # e.g., 'Pawn', 'Rook'
        self.color: str = color             # 'white' or 'black'
        self.position: Tuple = position     # e.g., (0, 0) for A8
        self.is_alive: bool = is_alive      # True if the piece is still in play

    def change_name(self, new_name: str) -> None:
        self.name = new_name

    def change_color(self, new_color: str) -> None:
        self.color = new_color

    def move(self, new_position) -> None:
        if not self.check_position(new_position):
            raise ValueError(f"Invalid position: {new_position}")
        self.position = new_position

    def vanish(self) -> None:
        self.is_alive = False

    def resurrect(self) -> None:
        self.is_alive = True

    @staticmethod
    def check_position(position: Tuple) -> bool:
        row, col = position
        return 0 <= row <= 7 and 0 <= col <= 7

    def __call__(self):
        return self

    def __str__(self) -> str:
        letter = list(self.dict_conversion_letter.keys())[list(self.dict_conversion_letter.values()).index(self.position[1])]
        number = list(self.dict_conversion_number.keys())[list(self.dict_conversion_number.values()).index(self.position[0])]
        return f"[WARNING]: Non-specific piece string called at position {letter}{number}."

    def __repr__(self) -> str:
        return f"[WARNING]: Non-specific piece representation called."