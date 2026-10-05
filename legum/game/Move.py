from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from legum.components.coords import coord_to_str, str_to_coord


@dataclass(frozen=True)
class Move:
    """
    A move from one square to another.
    Attributes:
        start (Tuple): (row, col) of the moving piece.
        end (Tuple): (row, col) of the target square. For castling, the king's target square.
        promotion (str | None): Short name of the piece a pawn promotes to ('Q', 'R', 'B' or 'N').
    """
    start: Tuple[int, int]
    end: Tuple[int, int]
    promotion: Optional[str] = None

    @property
    def uci(self) -> str:
        """Move in UCI notation, e.g. 'e2e4' or 'e7e8q'."""
        promotion = self.promotion.lower() if self.promotion else ""
        return f"{coord_to_str(self.start)}{coord_to_str(self.end)}{promotion}".lower()

    @classmethod
    def from_uci(cls, uci: str) -> Move:
        promotion = uci[4].upper() if len(uci) == 5 else None
        return cls(str_to_coord(uci[0:2]), str_to_coord(uci[2:4]), promotion)

    def __str__(self) -> str:
        return self.uci
