import os
import sys
from game.msgame import MSGame
from solver import MineSAT
from random import sample
from typing import Tuple, List, Optional
from time import sleep

#GAME = MSGame(8, 8, 10, 5684, "127.0.0.1")    # 8x8, 10 minutes: "Basic" preset
GAME = MSGame(16, 16, 40, 5684, "127.0.0.1")  # 16x16, 40 mines: "Intermediate" preset
#GAME = MSGame(30, 16, 99, 5684, "127.0.0.1")  # 16x30, 99 mines: "Advanced" preset
WIDTH = GAME.board.board_width
HEIGHT = GAME.board.board_height
# To keep track of tiles we don't want to pick, either discovered+safe or mine
UNDISCOVERED_TILES = set( (x, y) for x in range(1, WIDTH+1) for y in range(1, HEIGHT+1) )
# Mapping each entry in the numpy array to its character representation
GET_SYMBOL = '012345678..?'

# Cross-platform (Windows and POSIX, at least) screen clearing
clear_screen = lambda: os.system("cls" if os.name=="nt" else "clear")

def main():
    while True:
        clear_screen()
        print(GAME.get_board())

        if GAME.game_status == 1:
            print("[MESSAGE] YOU WIN!\n")
            break
        elif GAME.game_status == 0:
            print("[MESSAGE] YOU LOSE!\n")
            break

        # Create board representation for the solver
        board = update_board(GAME.board.info_map)
        solver = MineSAT(board)
        
        print("Options:")
        print("P) Play the game automatically!")
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
            flag_tile(moveX, moveY)
            continue
        elif move == "a":
            for moveY, moveX in solver.find_tiles("mine"):
                flag_tile(moveX-1, moveY-1)  # Adjust for 1-based indexing from the solver
            continue
        elif move == "u":
            moveY, moveX = get_coord_input()
            GAME.play_move("unflag", moveX, moveY)
            UNDISCOVERED_TILES.add( (moveX, moveY) )  # Allow the unflagged tile to be chosen randomly again
            continue
        elif move == "c":
            safe_tiles = solver.find_tiles()
            if not safe_tiles:
                print("There are no guaranteed safe tiles! :(\n")
            else:
                print("Guaranteed safe tiles:")
                for i, (y, x) in enumerate(safe_tiles):
                    print(f"{i}) Row: {y-1}, Column: {x-1}")
            moveY, moveX = get_coord_input()
        elif move == "r":
            move = pick_random_tile(solver.find_tiles("mine"))
            if move is None:
                print("ERROR: No more random tiles to choose!", file=sys.stderr)
                continue
            else:
                moveX = move[1]; moveY = move[0];
            moveX -= 1; moveY -= 1  # 1-indexed adjustment
        elif move == "p":
            # Auto-play the game
            auto_play()
            continue
        else:
            print("Invalid input. Stop that! >:(")
            continue

        GAME.play_move("click", moveX, moveY)


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


def update_board(np_game_board) -> List[str]:
    """
        Helper function to generate a string representation of the board.
        Also updates the set of unknown tiles, for use when randomly selecting tiles.
    """
    np_board = np_game_board
    board = ['' for j in range(HEIGHT)]
    for i in range(HEIGHT):
        for j in range(WIDTH):
            board[i] = board[i] + GET_SYMBOL[np_board[i][j]]
            # If we have a discovered tile, update our set
            if 0 <= np_board[i][j] <= 8:
                if (i+1, j+1) in UNDISCOVERED_TILES:  # np_board is 0-indexed, und_tiles is 1-indexed
                    UNDISCOVERED_TILES.remove( (i+1, j+1) )  # Throws a KeyError if (i, j) isn't in set
    return board


def flag_tile(moveX: int, moveY: int):
    """
        Helper function to flag a given tile.
    """
    GAME.play_move("flag", moveX, moveY)
    if (moveX, moveY) in UNDISCOVERED_TILES:
        UNDISCOVERED_TILES.remove( (moveX, moveY) )  # Prevent the flagged tile from being chosen randomly


def pick_random_tile(mine_tiles: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
    """
        Helper function to randomly select a tile after ensuring that its not a guaranteed mine.
    """
    for tile in mine_tiles:
        if tile in UNDISCOVERED_TILES:
            UNDISCOVERED_TILES.remove(tile)

    # Randomly get a tile from the now-updated UNDISCOVERED_TILES
    if UNDISCOVERED_TILES:
        moveY, moveX = sample(UNDISCOVERED_TILES, 1)[0]
    else:  # If there are no more undiscovered tiles, then return None to signify that there's nothing left
        return None

    if (moveX, moveY) in UNDISCOVERED_TILES:
        UNDISCOVERED_TILES.remove( (moveX, moveY) )
    return moveX, moveY

def auto_play(sleep_timer: float=2.0):
    """
        Automatically play the game.
    """
    while GAME.game_status == 2:  # In progress
        clear_screen()
        print(GAME.get_board())
        # First get the board state
        board = update_board(GAME.board.info_map)
        solver = MineSAT(board)

        # Find out if it can make any moves
        safe_tiles = solver.find_tiles()
        if not safe_tiles:  # If not, say a prayer and hope for the best
            mine_tiles = solver.find_tiles("mine")
            move = pick_random_tile(mine_tiles)
            if move is None:  # No more undiscovered tiles, flag the mine tiles and win!
                print("No more random tiles, flagging all mines")
                for moveY, moveX in mine_tiles:
                    GAME.play_move("flag", moveX-1, moveY-1)
            else:
                moveX = move[1]; moveY = move[0];
                print(f"Couldn't find a safe tile. Randomly clicking row {moveY-1}, column {moveX-1}")
                #print(UNDISCOVERED_TILES)
                GAME.play_move("click", moveX-1, moveY-1)
        else:  # Otherwise, play any safe moves
            for moveY, moveX in safe_tiles:
                print(f"Clicking row {moveY-1}, column {moveX-1}")
                GAME.play_move("click", moveX-1, moveY-1)  # The solver is 1-indexed, and is killing me softly
        sleep(sleep_timer)


# Moving the main routine to a function allows for function calls and such
# as opposed to a global routine, while still allowing global variables
if __name__ == "__main__":
    main()