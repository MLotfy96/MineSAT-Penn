# Overview
A solver for the game *Minesweeper* using Google's OR-Tools to locate any safe/mine tiles based on the current board state. Includes both a command-line interface and a graphical interface for the game that's integrated with the solver.

## What we've completed
### Solver
The most important part of this project is the Solver module itself. The solver is defined in the class `MineSAT`, and takes in a list of strings to represent the Minesweeper board. Each string represents a row on the board, and can be represented using the characters `012345678?`, where a numerical character represents a revealed tile with X number of adjacent mines, and `?` represents a hidden/unrevealed tile. This solver can be used free of the interfaces we provide for interactivity, should someone wish to include this solver in a different Minesweeper project.
Our Solver encoding is based on the work by Dennis Yurichev: https://yurichev.com/writings/SAT_SMT_by_example.pdf
### Command-line and Graphical Interfaces
Since the solver alone is pretty boring, we've created interfaces to interact with an actual version of the game that will automatically generate boards and allow the user to play Minesweeper, with the solver as a nice helper. To run these, run one of these two commands:
```
python3 simulator-cl.py
python3 simulator-gui.py
```
The command-line interface allows for: manually choosing tiles to reveal or flag (where the solver will tell you if there are any guaranteed tiles), randomly choosing a tile, or automatically playing the game using the solver. This version of Minesweeper requires that all mines be flagged, so you must flag all tiles to win.

The graphical interface was developed later, and doesn't allow for automatically playing the game like the command-line version does. However, it will highlight all guaranteed safe tiles in green. To play this version, left-click to reveal a tile, right-click to flag a tile.


# Installation
Our solver requires OR-Tools, while the underlying game (based on Minesweeper by Yuhuang Hu) requires `numpy` for internal use, and `pyqt` for the GUI:
```
pip install ortools numpy pyqt
```
If the command-line or graphical interface won't launch, try installing `minesweeper` as well.

## File Structure
**solver.py**: Contains the class for the Solver itself.

**simulator-cl.py**: The command-line interface for the game, includes the auto-play ability and demonstrates a bare-bones example of how one can interface with the game and use the solver as a helper.

**simulator-gui.py**: The graphical interface for the game, demonstrates how one can use the solver to interface with a graphical interface.

*game/* (directory): Contains the necessary files for the Minesweeper game, not necessary for the solver.

*test-solver.py*: Some nonsense for testing the solver, not super relevant.
