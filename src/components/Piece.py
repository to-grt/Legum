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
        move(new_position): Updates the piece's position.
        vanish(): Sets the piece's status to not alive.
        resurrect(): Sets the piece's status to alive.
        __str__(): Returns a string representation of the piece.
        __repr__(): Returns a detailed string representation of the piece.
    """

    dict_conversion_letter = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
    dict_conversion_number = {1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2, 7: 1, 8: 0}

    def __init__(self, color, position):
        self.name: str = "Piece"
        self.color: str = color             # 'white' or 'black'
        self.position: Tuple = position     # e.g., (0, 0) for A8
        self.is_alive: bool = True

    def move(self, new_position):
        self.position = new_position

    def vanish(self):
        self.is_alive = False

    def resurrect(self):
        self.is_alive = True

    def __str__(self):
        letter = list(self.dict_conversion_letter.keys())[list(self.dict_conversion_letter.values()).index(self.position[1])]
        number = list(self.dict_conversion_number.keys())[list(self.dict_conversion_number.values()).index(self.position[0])]
        return f"[WARNING]: Non-specific piece string called at position {letter}{number}."

    def __repr__(self):
        return f"[WARNING]: Non-specific piece representation called."