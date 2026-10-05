import argparse

from legum.components import Color
from legum.game import STARTING_FEN, GameState
from legum.gui import ChessGUI


def main():
    parser = argparse.ArgumentParser(prog="python -m legum", description="Play chess against Legum.")
    parser.add_argument("--ai", choices=["white", "black", "none"], default="black",
                        help="side played by the engine (default: black, 'none' for two human players)")
    parser.add_argument("--depth", type=int, default=3, help="engine search depth (default: 3)")
    parser.add_argument("--time", type=float, default=10.0, help="engine time limit per move in seconds (default: 10)")
    parser.add_argument("--fen", default=STARTING_FEN, help="starting position in FEN")
    args = parser.parse_args()

    ai_color = None if args.ai == "none" else Color(args.ai)
    ChessGUI(GameState(args.fen), ai_color=ai_color, ai_depth=args.depth, ai_time_limit=args.time).run()


if __name__ == "__main__":
    main()
