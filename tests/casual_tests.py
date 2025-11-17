from src.components import King, Board


def main():
    board = Board()
    print(board)


    king = King(board=board, color='white', position=(4, 4), is_alive=True)
    print(king)

    bad_king = King(board=board, color='black', position=(1, 7), is_alive=True)
    print(bad_king)


if __name__ == "__main__":
    main()
