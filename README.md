# Legum
A from-scratch chess engine :)

## Installation
Python 3.10 or newer.
```bash
pip install -e .          # numpy, pygame
pip install -e .[dev]     # + pytest, ruff, python-chess (used by the tests only)
```

## Play
```bash
python -m legum                    # you play white against the engine
python -m legum --ai white         # you play black
python -m legum --ai none          # two human players
python -m legum --depth 2          # weaker but faster engine (default depth: 3, max 10 s per move)
python -m legum --fen "<FEN>"      # start from any position
```
Click a piece, then one of the highlighted squares. `U` takes back a move, `N` starts a new game, `Esc` quits.

## Code layout
| Package | Content |
|---|---|
| `legum/components` | `Board` (piece placement, source of truth), `Piece` and its subclasses, `Color`, coordinates |
| `legum/game` | `GameState` (FEN, legal moves, make/unmake, end of game), `Move` (UCI notation), `perft` |
| `legum/engine` | Evaluation (material + piece-square tables) and negamax alpha-beta search with quiescence |
| `legum/gui` | Pygame interface |

Coordinates are `(row, col)` tuples, row 0 being rank 8 and column 0 file A.

## Tests
```bash
pytest              # fast tests (a few seconds)
pytest -m slow      # deep perft, 100 random games checked against python-chess, engine vs random player
ruff check .
```
The move generator is validated with [perft](https://www.chessprogramming.org/Perft_Results) on five reference
positions and by comparing legal moves, FEN, check and insufficient material with
[python-chess](https://github.com/niklasf/python-chess) along random games.

## Known simplifications
- The fifty-move rule and threefold repetition end the game automatically (under FIDE rules they must be claimed).
- For repetitions, an en passant square counts as soon as a pawn stands next to it, even if the capture is illegal
  because of a pin.
- The engine is written in pure Python: around 30 000 perft nodes per second on the development machine, depth 3 takes a few seconds.

See [PLAN.md](PLAN.md) for the roadmap.
