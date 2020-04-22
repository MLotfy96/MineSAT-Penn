from ortools.sat.python import cp_model
from typing import Optional, Tuple, List

# Special typing
Coordinate = Tuple[int, int]

class MineSAT:
    def __init__(self, board: List[str], num_solver_threads: int = 4):
        self.board = board
        self.length = len(board)
        self.width = len(board[0])
        self.threads = num_solver_threads


    def try_tile(self, row: int, col: int, find_safe: bool = True) -> Optional[Coordinate]:
        # Set up our "board", with space to place borders that will simplify calculations.
        # e.g. With a 9x9 board, internally we'll represent it as 11x11 with the extra rows always set to 0
        board = cp_model.CpModel()
        board_vars = [[board.NewBoolVar(f"Row {r}, Column {c} has a mine")
                        for c in range(self.width+2)]
                        for r in range(self.length+2)]
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
                    board.Add(board_vars[r][c] == 0)
                    board.Add(
                        board_vars[r-1][c-1] + board_vars[r-1][c] + board_vars[r-1][c+1] # Up-left, up, up-right
                        + board_vars[r][c-1] + board_vars[r][c+1] # Left, right
                        + board_vars[r+1][c-1] + board_vars[r+1][c] + board_vars[r+1][c+1] == int(tile) # Down-left, down, down-right
                    )

        if find_safe:
            # Place the mine
            board.Add(board_vars[row][col] == 1)
        else:
            # Place the "safe tile" (does that even make sense?)
            board.Add(board_vars[row][col] == 0)

        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = self.threads
        # We only want infeasible solutions, since it means the desired tile 100% cannot be placed in (row, col)
        if solver.Solve(board) == cp_model.INFEASIBLE:
            return (row, col)


    def find_tiles(self, tile_type: str = "safe") -> List[Coordinate]:
        if tile_type.lower() not in {"safe", "mine"}:
            raise ValueError(f'Tile type {tile_type} is not supported. Available types: "safe", "mine"')
        _find_safe = True if tile_type.lower()=="safe" else False

        found_tiles = []
        for r in range(self.length):
            for c in range(self.width):
                if self.board[r][c] == "?":
                    t = self.try_tile(r+1, c+1, find_safe=_find_safe)
                    if t is not None:
                        found_tiles.append(t)
        return found_tiles
