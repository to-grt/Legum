from legum.components import Color
from legum.game import GameState

# Piece-square tables, from white's point of view (row 0 = rank 8), in centipawns.
# Hand-written and untuned: they only nudge pieces towards sensible squares.
PAWN_TABLE = [
    [0,   0,   0,   0,   0,   0,   0,   0],
    [50,  50,  50,  50,  50,  50,  50,  50],
    [10,  10,  20,  30,  30,  20,  10,  10],
    [5,   5,   10,  25,  25,  10,  5,   5],
    [0,   0,   0,   20,  20,  0,   0,   0],
    [5,  -5,  -10,  0,   0,  -10, -5,   5],
    [5,   10,  10, -20, -20,  10,  10,  5],
    [0,   0,   0,   0,   0,   0,   0,   0],
]
KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20,   0,   0,   0,   0, -20, -40],
    [-30,   0,  10,  15,  15,  10,   0, -30],
    [-30,   5,  15,  20,  20,  15,   5, -30],
    [-30,   0,  15,  20,  20,  15,   0, -30],
    [-30,   5,  10,  15,  15,  10,   5, -30],
    [-40, -20,   0,   5,   5,   0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]
BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,  10,  10,   5,   0, -10],
    [-10,   5,   5,  10,  10,   5,   5, -10],
    [-10,   0,  10,  10,  10,  10,   0, -10],
    [-10,  10,  10,  10,  10,  10,  10, -10],
    [-10,   5,   0,   0,   0,   0,   5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]
ROOK_TABLE = [
    [0,   0,  0,  0,  0,  0,  0,  0],
    [5,  10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,   0,  0,  5,  5,  0,  0,  0],
]
QUEEN_TABLE = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10,   0,   0,  0,  0,   0,   0, -10],
    [-10,   0,   5,  5,  5,   5,   0, -10],
    [-5,    0,   5,  5,  5,   5,   0,  -5],
    [0,     0,   5,  5,  5,   5,   0,  -5],
    [-10,   5,   5,  5,  5,   5,   0, -10],
    [-10,   0,   5,  0,  0,   0,   0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]
KING_TABLE = [  # Middle game: stay behind the pawns, preferably castled
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20,   20,   0,   0,   0,   0,  20,  20],
    [20,   30,  10,   0,   0,  10,  30,  20],
]
KING_ENDGAME_TABLE = [  # Endgame: the king becomes an active piece
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10,   0,   0, -10, -20, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -30,   0,   0,   0,   0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50],
]
TABLES = {"P": PAWN_TABLE, "N": KNIGHT_TABLE, "B": BISHOP_TABLE, "R": ROOK_TABLE, "Q": QUEEN_TABLE}

# Below this much non-pawn material (both sides, centipawns), the king uses its endgame table
ENDGAME_MATERIAL = 1300


def evaluate(state: GameState) -> int:
    """
    Static evaluation in centipawns from the point of view of the side to move
    (positive = good for the player about to move), as negamax expects.
    """
    pieces = list(state.board.pieces())
    non_pawn_material = sum(piece.value for piece in pieces if piece.short_name not in ("P", "K"))
    king_table = KING_ENDGAME_TABLE if non_pawn_material <= ENDGAME_MATERIAL else KING_TABLE

    score = 0
    for piece in pieces:
        row, col = piece.position
        if piece.color is Color.BLACK:
            row = 7 - row  # Tables are written for white: mirror them vertically for black
        table = king_table if piece.short_name == "K" else TABLES[piece.short_name]
        piece_score = piece.value + table[row][col]
        score += piece_score if piece.color is Color.WHITE else -piece_score
    return score if state.turn is Color.WHITE else -score
