from legum.components import Board, King
from legum.gui import ChessGUI


def main():
    board = Board()
    board.place(King("white"), (7, 4))
    board.place(King("black"), (0, 4))
    print(board)
    ChessGUI(board_size=board.board_size).run(board)


if __name__ == "__main__":
    main()
