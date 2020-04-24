import os
from game.msgame import MSGame
from solver import MineSAT
from random import sample
from typing import Tuple

#game = MSGame(8, 8, 10, 5684, "127.0.0.1")    # 8x8, 10 minutes: "Basic" preset
game = MSGame(16, 16, 40, 5684, "127.0.0.1")  # 16x16, 40 mines: "Intermediate" preset
#game = MSGame(30, 16, 99, 5684, "127.0.0.1")  # 16x30, 99 mines: "Advanced" preset
WIDTH = game.board.board_width
HEIGHT = game.board.board_height
# To keep track of tiles we don't want to pick, either discovered+safe or mine
# TODO (maybe): Change UNDISCOVERED_TILES to 0-indexing? idk
UNDISCOVERED_TILES = set( (x, y) for x in range(1, WIDTH+1) for y in range(1, HEIGHT+1) )

get_symbol = '012345678..?'

# Cross-platform (Windows and POSIX, at least) screen clearing
clear_screen = lambda: os.system("cls" if os.name=="nt" else "clear")

def main():
    while True:
        clear_screen()
        print("Current state of the board:\n")
        print(game.get_board())

        if game.game_status == 1:
            print("[MESSAGE] YOU WIN!\n")
            break
        elif game.game_status == 0:
            print("[MESSAGE] YOU LOSE!\n")
            break

        # Create board representation for the solver
        np_board = game.board.info_map
        board = ['' for j in range(HEIGHT)]
        for i in range(HEIGHT):
            for j in range(WIDTH):
                board[i] = board[i] + get_symbol[np_board[i][j]]
                # If we have a discovered tile, update our set
                if 0 <= np_board[i][j] <= 8:
                    if (i+1, j+1) in UNDISCOVERED_TILES:  # np_board is 0-indexed, und_tiles is 1-indexed
                        UNDISCOVERED_TILES.remove( (i+1, j+1) )  # Throws a KeyError if (i, j) isn't in set

        solver = MineSAT(board)
        safe_tiles = solver.find_tiles()

        if len(safe_tiles) == 0:
            print("There are no guaranteed safe tiles! :(\n")
        else:
            print("Guaranteed safe tiles:")
            for i, (y, x) in enumerate(safe_tiles):
                print(f"{i}) Row: {y-1}, Column: {x-1}")
        
        print("\nAdditional options:")
        print("C) Choose a tile yourself!")
        print("F) Flag a tile!")
        print("A) Flag all guaranteed mine tiles!")
        print("U) Unflag a tile!")
        print("R) Pick a random tile!")

        # move is lowercased for ease of comparison
        move = input("\nPick a move: ").lower()

        # (Un)flagging is a special case where we use the different "flag" action, otherwise
        # our if/elif statements fall-through to the regular "click" action
        if move == "f":
            mine_tiles = solver.find_tiles("mine")
            if len(mine_tiles) > 0:
                print("Here are all the known mines: ")
                for x, y in mine_tiles:
                    print(f"Row {x-1}, Column {y-1}")
            moveY, moveX = get_coord_input()
            game.play_move("flag", moveX, moveY)
            if (moveX, moveY) in UNDISCOVERED_TILES:
                UNDISCOVERED_TILES.remove( (moveX, moveY) )  # Prevent the flagged tile from being chosen randomly
            continue
        elif move == "a":
            for moveY, moveX in solver.find_tiles("mine"):
                moveX -= 1; moveY -= 1  # 1-indexed adjustment
                game.play_move("flag", moveX, moveY)
                if (moveX, moveY) in UNDISCOVERED_TILES:
                    UNDISCOVERED_TILES.remove( (moveX, moveY) )  # Prevent the flagged tile from being chosen randomly
            continue
        elif move == "u":
            moveY, moveX = get_coord_input()
            game.play_move("unflag", moveX, moveY)
            UNDISCOVERED_TILES.add( (moveX, moveY) )  # Allow the unflagged tile to be chosen randomly again
            continue
        elif move == "c":
            moveY, moveX = get_coord_input()
        elif move == "r":
            for tile in solver.find_tiles("mine"):
                if tile in UNDISCOVERED_TILES:
                    UNDISCOVERED_TILES.remove(tile)
            # Randomly get a tile from the now-updated UNDISCOVERED_TILES
            moveY, moveX = sample(UNDISCOVERED_TILES, 1)[0]
            UNDISCOVERED_TILES.remove( (moveX, moveY) )
            moveX -= 1; moveY -= 1  # 1-indexed adjustment
        elif move.isdecimal() and 0 <= int(move) < len(safe_tiles):
            moveY, moveX = safe_tiles[int(move)]
            moveX -= 1; moveY -= 1  # 1-indexed adjustment
        else:
            print("Invalid input. Stop that! >:(")
            continue

        game.play_move("click", moveX, moveY)


def get_coord_input() -> Tuple[int, int]:
    """
        Gets the first two numbers from input, and repeats if
        necessary until the user actually enters two numbers.
    """
    usr_input = input("Enter the tile's coordinates in row, col order: ").replace(",", " ").replace(";", " ").split(" ")
    i = 0
    pair = []
    while True:
        for item in usr_input:
            if item.isdecimal():
                pair.append(int(item))
                i += 1
            if i == 2: return tuple(pair)
        # If we make it here, we didn't get two numbers and have to restart. Bad user! >:(
        pair.clear()
        i = 0
        usr_input = input("ERROR: No valid coordinate pair found.\nEnter the tile's coordinates in row, col order: ").replace(",", " ").replace(";", " ").split(" ")


# Moving the main routine to a function allows for function calls and such
# as opposed to a global routine, while still allowing global variables
if __name__ == "__main__":
    main()