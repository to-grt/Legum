# Queen.py


# Imports
import numpy as np
from Legum.Piece import Piece


class Queen(Piece):

    def __init__(self, color: int, position: tuple) -> None:
        super().__init__()
        self.name = "Queen"
        self.color = color
        self.position = position
        self.is_alive = True


    def __repr__(self) -> str:
        return f"<Knight {self.color} {self.position} {self.is_alive}>"

    def __str__(self) -> str:
        return f"Knight {self.color}"

    def __call__(self) -> list:
        return self.get_moves_from_direction_vectors()

    def get_moves_from_direction_vectors(self) -> list:

        vectors = np.arange(0, 8)
        


        pass

