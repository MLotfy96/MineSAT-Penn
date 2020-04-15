from ortools.sat.python import cp_model
from typing import Optional, Tuple, List

_CLEAN_99_BOARD = [
    "????????",
    "????????",
    "????????",
    "????????",
    "????????",
    "????????",
    "????????",
    "????????"
]

_TEST_BOARD = [
    "????????",
    "????????",
    "?2???3??",
    "????1111",
    "?1??1000",
    "??2?1000",
    "????1111",
    "?????1??"
]

_CHALLENGE_BOARD = [
    '??????',
    '???2??',
    '???4??',
    '?2??2?',
    '?2222?',
    '?1001?'
]

# Special typing
Coordinates = Tuple[int, int]

class MineSAT:
    def __init__(self, board: List[str], num_solver_threads: int = 4):
        self.board = board
        self.length = len(board)
        self.width = len(board[0])
        self.threads = num_solver_threads

    def try_tile(self, row: int, col: int) -> Optional[Coordinates]:
        # Don't try to place a mine on a known tile
        if self.board[row][col] != "?": return 

        # Set up our "board", with space to place borders that will simplify calculations.
        # e.g. With a 9x9 board, internally we'll represent it as 11x11 with the extra rows always set to 0
        board = cp_model.CpModel()
        board_vars = [[board.NewBoolVar(f"Row {r}, Column {c} has a mine") for c in range(self.width+2)] for r in range(self.length+2)]
        # Create the border
        for c in range(self.width+2):
            board.Add(board_vars[0][c] == 0)
            board.Add(board_vars[self.length+1][c] == 0)
        for r in range(self.length+2):
            board.Add(board_vars[r][0] == 0)
            board.Add(board_vars[r][self.width+1] == 0)

        # For each known tile on the board, we'll add constraints that enforce
        # that the number of mines adjacent equals the value on the tile. 
        # Note that "adjacent" in MS includes the diagonals as well as cardinals.
        for r, _row in enumerate(self.board, start=1):
            for c, tile in enumerate(_row, start=1):
                if tile in "012345678":
                    board.Add(
                        board_vars[r-1][c-1] + board_vars[r-1][c] + board_vars[r-1][c+1] # Up-left, up, up-right
                        + board_vars[r][c-1] + board_vars[r][c+1] # Left, right
                        + board_vars[r+1][c-1] + board_vars[r+1][c] + board_vars[r+1][c+1] == int(tile) # Down-left, down, down-right
                    )

        # Place the mine
        board.Add(board_vars[row][col] == 1)

        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = self.threads
        # We only want infeasible solutions, since it means a mine 100% cannot be placed in (row, col)
        if solver.Solve(board) == cp_model.INFEASIBLE:
            return (row, col)

    def find_safe_tiles(self) -> List[Coordinates]:
        safe_tiles = []
        for r in range(self.length):
            for c in range(self.width):
                if self.board[r][c] == "?":
                    t = self.try_tile(r+1, c+1)
                    if t is not None:
                        safe_tiles.append(t)
        return safe_tiles

if __name__ == "__main__":
    MS = MineSAT(_TEST_BOARD)
    tiles = MS.find_safe_tiles()
    print(tiles)