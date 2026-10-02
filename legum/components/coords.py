from typing import Tuple

FILES = "ABCDEFGH"


def coord_to_str(position: Tuple[int, int], board_size: int = 8) -> str:
    """
    Converts a (row, col) tuple to standard chess notation.
    Row 0 is the top of the board (rank 8 on a standard board), column 0 is file A.
    >>> coord_to_str((7, 0))
    'A1'
    """
    row, col = position
    return f"{FILES[col]}{board_size - row}"


def str_to_coord(name: str, board_size: int = 8) -> Tuple[int, int]:
    """
    Converts a square name (case insensitive) to a (row, col) tuple.
    >>> str_to_coord("e4")
    (4, 4)
    """
    col = FILES.index(name[0].upper())
    row = board_size - int(name[1:])
    return row, col
