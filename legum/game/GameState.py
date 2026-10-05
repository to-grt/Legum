from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from legum.components import PIECE_CLASSES, Bishop, Board, Color, King, Knight, Pawn, Piece, Rook
from legum.components.coords import coord_to_str, str_to_coord

from .Move import Move

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PROMOTION_CHOICES = ("Q", "R", "B", "N")

# Castling data for a standard 8x8 board, keyed by the FEN castling letter:
# (king start, king end, rook start, rook end, squares that must be empty, squares the king crosses)
CASTLING = {
    "K": ((7, 4), (7, 6), (7, 7), (7, 5), [(7, 5), (7, 6)], [(7, 5), (7, 6)]),
    "Q": ((7, 4), (7, 2), (7, 0), (7, 3), [(7, 1), (7, 2), (7, 3)], [(7, 3), (7, 2)]),
    "k": ((0, 4), (0, 6), (0, 7), (0, 5), [(0, 5), (0, 6)], [(0, 5), (0, 6)]),
    "q": ((0, 4), (0, 2), (0, 0), (0, 3), [(0, 1), (0, 2), (0, 3)], [(0, 3), (0, 2)]),
}
# Moving from or capturing on one of these squares removes the matching castling rights
CASTLING_SQUARES = {(7, 4): "KQ", (7, 7): "K", (7, 0): "Q", (0, 4): "kq", (0, 7): "k", (0, 0): "q"}

KNIGHT_STEPS = Knight.directions
KING_STEPS = King.directions
ORTHOGONAL = Rook.directions
DIAGONAL = Bishop.directions


@dataclass(frozen=True)
class Outcome:
    """End of a game. `result` is '1-0', '0-1' or '1/2-1/2'."""
    result: str
    reason: str
    winner: Optional[Color] = None


@dataclass
class _Undo:
    """Everything needed to take a move back."""
    move: Move
    piece: Piece
    captured: Optional[Piece]
    captured_square: Optional[Tuple[int, int]]
    castling: str
    en_passant: Optional[Tuple[int, int]]
    halfmove_clock: int
    fullmove_number: int
    rook_move: Optional[Tuple[Tuple[int, int], Tuple[int, int]]]


class GameState:
    """
    A full chess position (FEN), its legal moves and the game history.
    Attributes:
        board (Board): Piece placement.
        turn (Color): Side to move.
        castling (str): Remaining castling rights as in FEN ('KQkq', '' when none).
        en_passant (Tuple | None): Square a pawn can capture en passant onto.
        halfmove_clock (int): Half-moves since the last capture or pawn move (fifty-move rule).
        fullmove_number (int): Starts at 1, incremented after each black move.
    Methods:
        set_fen(fen) / fen(): Load / export a position in Forsyth-Edwards Notation.
        legal_moves(): All legal moves of the side to move.
        make_move(move) / unmake_move(): Play / take back a move, without legality check (fast, for search).
        play(move): Plays a move after checking it is legal.
        outcome(): The end of the game (checkmate, stalemate, draws) or None while it goes on.
    """

    def __init__(self, fen: str = STARTING_FEN) -> None:
        self.board = Board(8)
        self.set_fen(fen)

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- FEN ----------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def set_fen(self, fen: str) -> None:
        fields = fen.split()
        if len(fields) == 4:
            fields += ["0", "1"]
        if len(fields) != 6:
            raise ValueError(f"FEN '{fen}' must have 6 fields.")
        placement, turn, castling, en_passant, halfmove, fullmove = fields
        self.board.set_placement(placement)
        if turn not in ("w", "b"):
            raise ValueError(f"Side to move '{turn}' must be 'w' or 'b'.")
        self.turn = Color.WHITE if turn == "w" else Color.BLACK
        if castling != "-" and (not set(castling) <= set("KQkq")):
            raise ValueError(f"Castling rights '{castling}' are not valid.")
        self.castling = "".join(right for right in "KQkq" if right in castling)
        self.en_passant = None if en_passant == "-" else str_to_coord(en_passant)
        self.halfmove_clock = int(halfmove)
        self.fullmove_number = int(fullmove)

        self.kings: Dict[Color, Tuple[int, int]] = {}
        for piece in self.board.pieces():
            if isinstance(piece, King):
                if piece.color in self.kings:
                    raise ValueError(f"FEN '{fen}' has more than one {piece.color.value} king.")
                self.kings[piece.color] = piece.position
        if len(self.kings) != 2:
            raise ValueError(f"FEN '{fen}' must have exactly one king per side.")

        self.history: List[_Undo] = []
        self.position_keys: List[str] = [self._position_key()]

    def fen(self) -> str:
        en_passant = coord_to_str(self.en_passant).lower() if self.en_passant else "-"
        return (f"{self.board.placement()} {self.turn.prefix} {self.castling or '-'} {en_passant} "
                f"{self.halfmove_clock} {self.fullmove_number}")

    def _position_key(self) -> str:
        """
        Identifies a position for the repetition rule: placement, side to move, castling rights and
        en passant square, the latter only when a pawn of the side to move stands next to it
        (simplification: a capture that would be illegal because of a pin still counts).
        """
        en_passant = "-"
        if self.en_passant is not None:
            row, col = self.en_passant
            pawn_row = row + (1 if self.turn is Color.WHITE else -1)  # Pawns of the side to move
            for d_col in (-1, 1):
                square = (pawn_row, col + d_col)
                if self.board.check_position(square):
                    piece = self.board[square]
                    if isinstance(piece, Pawn) and piece.color is self.turn:
                        en_passant = coord_to_str(self.en_passant)
        return f"{self.board.placement()} {self.turn.prefix} {self.castling} {en_passant}"

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Attacks ------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def is_square_attacked(self, square: Tuple[int, int], by_color: Color) -> bool:
        """True if a piece of `by_color` attacks `square` (whether or not that square is occupied)."""
        grid = self.board.board
        size = self.board.board_size
        row, col = square

        def piece_at(r: int, c: int) -> Optional[Piece]:
            return grid[r, c] if 0 <= r < size and 0 <= c < size else None

        # Pawns attack diagonally forward, so look one row "behind" the square from the attacker's point of view
        pawn_row = row + 1 if by_color is Color.WHITE else row - 1
        for d_col in (-1, 1):
            piece = piece_at(pawn_row, col + d_col)
            if piece is not None and piece.color is by_color and piece.short_name == "P":
                return True
        for steps, name in ((KNIGHT_STEPS, "N"), (KING_STEPS, "K")):
            for d_row, d_col in steps:
                piece = piece_at(row + d_row, col + d_col)
                if piece is not None and piece.color is by_color and piece.short_name == name:
                    return True
        for directions, names in ((ORTHOGONAL, ("R", "Q")), (DIAGONAL, ("B", "Q"))):
            for d_row, d_col in directions:
                r, c = row + d_row, col + d_col
                while 0 <= r < size and 0 <= c < size:
                    piece = grid[r, c]
                    if piece is not None:
                        if piece.color is by_color and piece.short_name in names:
                            return True
                        break
                    r, c = r + d_row, c + d_col
        return False

    def in_check(self, color: Optional[Color] = None) -> bool:
        color = color or self.turn
        return self.is_square_attacked(self.kings[color], color.opposite)

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Move generation ----------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def pseudo_legal_moves(self) -> List[Move]:
        """Moves that follow the piece rules but may leave the own king in check."""
        moves = []
        last_row = {Color.WHITE: 0, Color.BLACK: self.board.board_size - 1}[self.turn]
        for piece in list(self.board.pieces(self.turn)):
            start = piece.position
            if isinstance(piece, Pawn):
                for end in piece.find_moves(self.board, self.en_passant):
                    if end[0] == last_row:
                        moves.extend(Move(start, end, promotion) for promotion in PROMOTION_CHOICES)
                    else:
                        moves.append(Move(start, end))
            else:
                moves.extend(Move(start, end) for end in piece.find_moves(self.board))
        moves.extend(self._castling_moves())
        return moves

    def _castling_moves(self) -> List[Move]:
        moves = []
        for right in self.castling:
            if right.isupper() != (self.turn is Color.WHITE):
                continue
            king_start, king_end, rook_start, _, must_be_empty, king_path = CASTLING[right]
            king, rook = self.board[king_start], self.board[rook_start]
            if not (isinstance(king, King) and king.color is self.turn):
                continue
            if not (isinstance(rook, Rook) and rook.color is self.turn):
                continue
            if any(self.board[square] is not None for square in must_be_empty):
                continue
            opponent = self.turn.opposite
            if self.is_square_attacked(king_start, opponent):
                continue
            if any(self.is_square_attacked(square, opponent) for square in king_path):
                continue
            moves.append(Move(king_start, king_end))
        return moves

    def legal_moves(self) -> List[Move]:
        moves = []
        color = self.turn
        for move in self.pseudo_legal_moves():
            self.make_move(move)
            if not self.is_square_attacked(self.kings[color], color.opposite):
                moves.append(move)
            self.unmake_move()
        return moves

    def is_legal(self, move: Move) -> bool:
        return move in self.legal_moves()

    def is_capture(self, move: Move) -> bool:
        target = self.board[move.end]
        if target is not None:
            return True
        return move.end == self.en_passant and isinstance(self.board[move.start], Pawn)

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Making and unmaking moves ------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def make_move(self, move: Move) -> None:
        """Plays a move without checking that it is legal. Use play() for moves coming from a user."""
        board = self.board
        piece = board[move.start]
        if piece is None:
            raise ValueError(f"No piece on {coord_to_str(move.start)} for move {move}.")

        captured_square = move.end
        if isinstance(piece, Pawn) and move.end == self.en_passant and board[move.end] is None:
            captured_square = (move.start[0], move.end[1])
        captured = board.remove(captured_square)

        rook_move = None
        if isinstance(piece, King) and abs(move.end[1] - move.start[1]) == 2:
            rook_col_start, rook_col_end = (7, 5) if move.end[1] > move.start[1] else (0, 3)
            rook_move = ((move.start[0], rook_col_start), (move.start[0], rook_col_end))

        self.history.append(_Undo(move, piece, captured, captured_square if captured else None,
                                  self.castling, self.en_passant, self.halfmove_clock, self.fullmove_number,
                                  rook_move))

        board.move_piece(move.start, move.end)
        if rook_move is not None:
            board.move_piece(*rook_move)
        if move.promotion is not None:
            board.remove(move.end)
            board.place(PIECE_CLASSES[move.promotion](piece.color), move.end)
        if isinstance(piece, King):
            self.kings[piece.color] = move.end

        if isinstance(piece, Pawn) and abs(move.end[0] - move.start[0]) == 2:
            self.en_passant = ((move.start[0] + move.end[0]) // 2, move.start[1])
        else:
            self.en_passant = None
        for square in (move.start, move.end):
            lost_rights = CASTLING_SQUARES.get(square)
            if lost_rights:
                self.castling = "".join(right for right in self.castling if right not in lost_rights)

        self.halfmove_clock = 0 if isinstance(piece, Pawn) or captured is not None else self.halfmove_clock + 1
        if self.turn is Color.BLACK:
            self.fullmove_number += 1
        self.turn = self.turn.opposite
        self.position_keys.append(self._position_key())

    def unmake_move(self) -> Move:
        """Takes back the last move and returns it."""
        undo = self.history.pop()
        self.position_keys.pop()
        board = self.board
        move = undo.move

        board.remove(move.end)  # The moved piece, or the promoted one
        board.place(undo.piece, move.start)
        if undo.rook_move is not None:
            rook_start, rook_end = undo.rook_move
            board.move_piece(rook_end, rook_start)
        if undo.captured is not None:
            board.place(undo.captured, undo.captured_square)
        if isinstance(undo.piece, King):
            self.kings[undo.piece.color] = move.start

        self.castling = undo.castling
        self.en_passant = undo.en_passant
        self.halfmove_clock = undo.halfmove_clock
        self.fullmove_number = undo.fullmove_number
        self.turn = self.turn.opposite
        return move

    def play(self, move: Move | str) -> Move:
        """Plays a move given as a Move or in UCI notation, after checking it is legal."""
        if isinstance(move, str):
            move = Move.from_uci(move)
        if not self.is_legal(move):
            raise ValueError(f"Illegal move {move} in position {self.fen()}.")
        self.make_move(move)
        return move

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- End of the game ----------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------- #
    def is_checkmate(self) -> bool:
        return self.in_check() and not self.legal_moves()

    def is_stalemate(self) -> bool:
        return not self.in_check() and not self.legal_moves()

    def is_insufficient_material(self) -> bool:
        """
        Neither side can ever checkmate: only kings, plus either a single knight or bishop,
        or any number of bishops all standing on squares of the same color.
        """
        minors = []
        for piece in self.board.pieces():
            if isinstance(piece, King):
                continue
            if not isinstance(piece, (Knight, Bishop)):
                return False
            minors.append(piece)
        if len(minors) <= 1:
            return True
        if all(isinstance(piece, Bishop) for piece in minors):
            return len({sum(piece.position) % 2 for piece in minors}) == 1
        return False

    def is_fifty_moves(self) -> bool:
        return self.halfmove_clock >= 100

    def is_threefold_repetition(self) -> bool:
        return self.position_keys.count(self.position_keys[-1]) >= 3

    def outcome(self) -> Optional[Outcome]:
        """
        Returns how the game ended, or None if it goes on.
        Simplification: the fifty-move rule and threefold repetition end the game automatically,
        whereas under FIDE rules a player has to claim them.
        """
        if not self.legal_moves():
            if self.in_check():
                winner = self.turn.opposite
                return Outcome("1-0" if winner is Color.WHITE else "0-1", "checkmate", winner)
            return Outcome("1/2-1/2", "stalemate")
        if self.is_insufficient_material():
            return Outcome("1/2-1/2", "insufficient material")
        if self.is_fifty_moves():
            return Outcome("1/2-1/2", "fifty-move rule")
        if self.is_threefold_repetition():
            return Outcome("1/2-1/2", "threefold repetition")
        return None

    def __str__(self) -> str:
        return f"{self.board}\n{self.fen()}"
