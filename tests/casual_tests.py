from src.components import King, Board


def main():
    board = Board()
    print(board)


    king = King(board=board, color='white', position=(4, 4), is_alive=True)
    print(king)

    king_moves = king.find_moves(board)
    king.print_moves_nicely(king_moves)


if __name__ == "__main__":
    main()
