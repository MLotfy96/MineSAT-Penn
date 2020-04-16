from game.msgame import MSGame
from solver import MineSAT
from random import randint

game = MSGame(10, 10, 5, 5680, "127.0.0.1")
width = game.board.board_width
height = game.board.board_height

get_symbol = '012345678..?'

while True:
    print("Current state of the board:\n")
    print(game.get_board())

    if game.game_status == 1:
        print("[MESSAGE] YOU WIN!\n")
        break
    elif game.game_status == 0:
        print("[MESSAGE] YOU LOSE!\n")
        break

    np_board = game.board.info_map
    board = ['' for j in range(height)]
    for i in range(width):
        for j in range(height):
            board[i] = board[i] + get_symbol[np_board[i][j]]

    solver = MineSAT(board)
    safe_tiles = solver.find_safe_tiles()

    if len(safe_tiles) == 0:
        print("There is no guaranteed safe tiles! :(\n")
        print("Options:")
        print("0) Make a random move!")
    else:
        print("Guaranteed safe tiles:")
        i = 0
        for (x, y) in safe_tiles:
            print(i, ") Row: ", x - 1, ", Column: ", y - 1)
            i += 1

    move = input("\nPick a move!\n")
    print("\n")
    moveX = 0
    moveY = 0

    # Picking a random tile
    if len(safe_tiles) == 0:
        moveX = randint(0, width - 1)
        moveY = randint(0, height - 1)
    # Getting the position of the decided move
    else:
        moveY, moveX = safe_tiles[int(move)]
        moveY -= 1
        moveX -= 1

    game.play_move("click", moveX, moveY)

    # The game never ends, we still need to develop a "find_mines"
    # function in the MineSAT class in order to flag the mines
    # and finish the game. But the solver works perfectly until
    # all remaining tiles are mines.