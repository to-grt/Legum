"""
UCI (Universal Chess Interface) front-end, so that Legum can be used by any UCI chess GUI or tool
(Arena, cutechess-cli, python-chess, a Lichess bot...).
Protocol description: https://gist.github.com/DOBRO/2592c6dad754ba67e6dcaec8c90165bf

Run it with `python -m legum.uci` or the `legum-uci` command.
"""
import sys
import threading
import time
from typing import List, Optional, TextIO

from legum.components import Color
from legum.engine import MATE_SCORE, Searcher, SearchResult
from legum.game import GameState, Move

ENGINE_NAME = "Legum"
ENGINE_AUTHOR = "Legum contributors"
DEFAULT_DEPTH = 3
MAX_DEPTH = 64


class UCIEngine:
    """
    Reads UCI commands line by line and writes the answers.
    The search runs in a thread so that `stop`, `isready` and `quit` are answered while it thinks.
    Supported commands: uci, isready, ucinewgame, position, go, stop, quit. Unknown commands are ignored,
    as the protocol requires.
    """

    def __init__(self, output: TextIO = sys.stdout) -> None:
        self.output = output
        self.state = GameState()
        self.searcher = Searcher()
        self._search_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def send(self, line: str) -> None:
        with self._lock:
            self.output.write(line + "\n")
            self.output.flush()

    def run(self, input_stream: TextIO = sys.stdin) -> None:
        """
        Processes commands until `quit` (which interrupts a running search) or the end of the input
        (which lets it finish, handy for `echo "go depth 4" | legum-uci`).
        """
        for line in input_stream:
            if not self.handle(line):
                self.stop_search()
                return
        self.wait_search()

    def handle(self, line: str) -> bool:
        """Processes one command. Returns False when the engine must quit."""
        tokens = line.split()
        if not tokens:
            return True
        command, args = tokens[0], tokens[1:]

        if command == "quit":
            return False
        if command == "stop":
            self.stop_search()
            return True
        if command == "isready":
            self.send("readyok")
            return True

        self.wait_search()  # Other commands must not change the position under a running search
        if command == "uci":
            self.send(f"id name {ENGINE_NAME}")
            self.send(f"id author {ENGINE_AUTHOR}")
            self.send("uciok")
        elif command == "ucinewgame":
            self.state = GameState()
        elif command == "position":
            self.set_position(args)
        elif command == "go":
            self.go(args)
        return True

    # --------------------------------------------------------------------------------------------------------------- #
    # ----------- Commands ------------------------------------------------------------------------------------------ #
    # --------------------------------------------------------------------------------------------------------------- #
    def set_position(self, args: List[str]) -> None:
        """position [startpos | fen <6 fields>] [moves <move1> ... <movei>]"""
        moves_index = args.index("moves") if "moves" in args else len(args)
        setup, moves = args[:moves_index], args[moves_index + 1:]
        try:
            if setup and setup[0] == "fen":
                state = GameState(" ".join(setup[1:]))
            else:
                state = GameState()
            for uci in moves:
                state.play(Move.from_uci(uci))
        except ValueError as error:
            self.send(f"info string invalid position: {error}")
            return
        self.state = state

    def go(self, args: List[str]) -> None:
        """go [depth <n>] [movetime <ms>] [wtime <ms> btime <ms> winc <ms> binc <ms> movestogo <n>] [infinite]"""
        options = {}
        for name in ("depth", "movetime", "wtime", "btime", "winc", "binc", "movestogo"):
            if name in args:
                index = args.index(name)
                try:
                    options[name] = int(args[index + 1])
                except (IndexError, ValueError):
                    self.send(f"info string invalid value for {name}")
                    return
        depth, time_limit = self.search_limits(options, infinite="infinite" in args)

        # The search works on its own copy, so a later `position` command cannot interfere with it
        state = GameState(self.state.fen())
        state.position_keys = list(self.state.position_keys)
        start = time.monotonic()

        def report(result: SearchResult) -> None:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            self.send(f"info depth {result.depth} score {format_score(result.score)} nodes {result.nodes} "
                      f"time {elapsed_ms} pv {result.move.uci}")

        def think() -> None:
            result = self.searcher.search(state, depth, time_limit, on_iteration=report)
            # "0000" is the null move, sent when there is no legal move (checkmate or stalemate)
            self.send(f"bestmove {result.move.uci if result.move else '0000'}")

        self._search_thread = threading.Thread(target=think, daemon=True)
        self._search_thread.start()

    def search_limits(self, options: dict, infinite: bool):
        """Turns the `go` options into a (depth, time limit in seconds) pair."""
        if infinite:
            return MAX_DEPTH, None
        if "movetime" in options:
            return options.get("depth", MAX_DEPTH), options["movetime"] / 1000
        white = self.state.turn is Color.WHITE
        remaining = options.get("wtime" if white else "btime")
        if remaining is not None:
            increment = options.get("winc" if white else "binc", 0)
            moves_to_go = options.get("movestogo", 30)
            # Simple time management: an equal share of the remaining time, plus most of the increment,
            # never more than half of what is left
            budget = min(remaining / max(moves_to_go, 1) + increment * 0.8, remaining / 2)
            return options.get("depth", MAX_DEPTH), max(budget, 10) / 1000
        return options.get("depth", DEFAULT_DEPTH), None

    def stop_search(self) -> None:
        if self._search_thread is not None:
            self.searcher.stop()
        self.wait_search()

    def wait_search(self) -> None:
        if self._search_thread is not None:
            self._search_thread.join()
            self._search_thread = None


def format_score(score: int) -> str:
    """UCI score: 'cp <centipawns>', or 'mate <moves>' (negative when the engine is getting mated)."""
    if abs(score) > MATE_SCORE - 1000:
        plies = MATE_SCORE - abs(score)
        moves = (plies + 1) // 2
        return f"mate {moves if score > 0 else -moves}"
    return f"cp {score}"


def main() -> None:
    UCIEngine().run()


if __name__ == "__main__":
    main()
