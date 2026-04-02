# Sokoban

A terminal-based Sokoban puzzle game with a built-in BFS auto-solver.

## Tile Legend

| Symbol | Meaning |
|--------|---------|
| `#` | Wall |
| `@` | Pusher |
| `+` | Pusher on Goal |
| `$` | Box |
| `*` | Box on Goal |
| `.` | Goal |
| ` ` | Floor (space) |

## How to Run

```
python Sokoban.py
```

You will be prompted for:
1. **Mode** — `play` (manual) or `solve` (auto BFS solver)
2. **Raw string** — the level in `<width>:<data>` format

### Example Level

```
6:###### @ $.######
```

This represents a 6-wide grid:
```
######
# @$.#
######
```

## Modes

### Play (Task A)

Move the pusher (`@`) to push all boxes (`$`) onto goals (`.`).

| Key | Direction |
|-----|-----------|
| `W` | Up |
| `A` | Left |
| `S` | Down |
| `D` | Right |
| `Q` | Quit |

The level is solved when no bare `$` tiles remain (all boxes are on goals, shown as `*`).

### Solve (Task B)

The BFS solver automatically finds the shortest solution by exploring every possible move, layer by layer. Once found, the solution is played back step by step in the terminal.

## How BFS Works

1. Start with the initial board in a queue
2. Pop the oldest state (fewest moves)
3. Try all 4 directions — if a move solves the puzzle, return that path
4. Otherwise, if the resulting state hasn't been seen before, add it to the queue
5. Repeat until solved or queue is empty (unsolvable)

Because BFS processes states in order of move count (first-in, first-out), the first solution found is guaranteed to be the shortest.

## Files

| File | Description |
|------|-------------|
| `Sokoban.py` | Main game script |
| `Sokoban.ipynb` | Jupyter Notebook version |
