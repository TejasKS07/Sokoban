"""
Sokoban - Base Template
=======================
Task A: Playable engine  (fill in the TODOs)
Task B: BFS auto-solver  (fill in the TODOs)

Tile legend
-----------
#   Wall
@   Pusher
+   Pusher on Goal
$   Box
*   Box on Goal
.   Goal
    Floor (space)
"""

import os
import time
from collections import deque


WALL    = '#'
PUSHER  = '@'
PUSHER_ON_GOAL = '+'
BOX     = '$'
BOX_ON_GOAL    = '*'
GOAL    = '.'
FLOOR   = ' '

# Direction vectors: (row_delta, col_delta)
DIRECTIONS = {
    'U': (-1,  0),
    'D': ( 1,  0),
    'L': ( 0, -1),
    'R': ( 0,  1),
}

# ─────────────────────────────────────────────
# 2.  LEVEL LOADING
# ─────────────────────────────────────────────

def parse_level(raw_string: str) -> list[list[str]]:
    """
    Parse a raw-string level into a 2-D grid (list of lists).

    Format:  "<width>:<data>"
    Example: "6:###### @ $.######"
    """
    colon_idx = raw_string.index(':')
    width = int(raw_string[:colon_idx])
    data  = raw_string[colon_idx + 1:]

    grid = []
    for i in range(0, len(data), width):
        grid.append(list(data[i:i + width]))
    return grid


def find_positions(grid: list[list[str]]) -> tuple:
    """
    Scan the grid and return:
        pusher_pos  : (row, col)
        box_positions : frozenset of (row, col)
        goal_positions: frozenset of (row, col)

    Remember: '+' means pusher ON a goal, '*' means box ON a goal.
    Both count toward goal_positions.
    Both count toward pusher / box positions respectively.
    """
    pusher_pos    = None
    box_positions = set()
    goal_positions = set()

    for r, row in enumerate(grid):
        for c, tile in enumerate(row):
            if tile == PUSHER:
                pusher_pos = (r, c)
            elif tile == PUSHER_ON_GOAL:
                pusher_pos = (r, c)
                goal_positions.add((r, c))
            elif tile == BOX:
                box_positions.add((r, c))
            elif tile == BOX_ON_GOAL:
                box_positions.add((r, c))
                goal_positions.add((r, c))
            elif tile == GOAL:
                goal_positions.add((r, c))

    return pusher_pos, frozenset(box_positions), frozenset(goal_positions)


# ─────────────────────────────────────────────
# 3.  RENDERING
# ─────────────────────────────────────────────

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def render(grid: list[list[str]]):
    """Print the current grid to the terminal."""
    clear_screen()
    for row in grid:
        print(''.join(row))
    print()  # blank line after board


# ─────────────────────────────────────────────
# 4.  GAME STATE  (pure functions — no mutation)
# ─────────────────────────────────────────────

def is_walkable(tile: str) -> bool:
    """Return True if the pusher can step onto this tile."""
    return tile in (FLOOR, GOAL)


def is_box(tile: str) -> bool:
    return tile in (BOX, BOX_ON_GOAL)


def apply_move(grid: list[list[str]], direction: str) -> list[list[str]] | None:
    """
    Attempt to move the pusher in `direction`.
    Returns a NEW grid (deep copy) if the move is legal, else None.
    """
    import copy

    # 1. Find the pusher
    pusher_r, pusher_c = None, None
    for r, row in enumerate(grid):
        for c, tile in enumerate(row):
            if tile in (PUSHER, PUSHER_ON_GOAL):
                pusher_r, pusher_c = r, c
                break
        if pusher_r is not None:
            break

    dr, dc = DIRECTIONS[direction]
    target_r, target_c = pusher_r + dr, pusher_c + dc
    target_tile = grid[target_r][target_c]

    # 3. Wall check
    if target_tile == WALL:
        return None

    # 4. Box push check
    if is_box(target_tile):
        beyond_r, beyond_c = target_r + dr, target_c + dc
        beyond_tile = grid[beyond_r][beyond_c]
        if not is_walkable(beyond_tile):
            return None  # can't push box into wall or another box
    else:
        if not is_walkable(target_tile):
            return None  # target not walkable and not a box

    # All checks passed — make the move on a copy
    new_grid = copy.deepcopy(grid)

    # 6. Restore tile the pusher is leaving
    if grid[pusher_r][pusher_c] == PUSHER_ON_GOAL:
        new_grid[pusher_r][pusher_c] = GOAL
    else:
        new_grid[pusher_r][pusher_c] = FLOOR

    # 8. If pushing a box, place it in the beyond cell
    if is_box(target_tile):
        beyond_r, beyond_c = target_r + dr, target_c + dc
        beyond_tile = grid[beyond_r][beyond_c]
        if beyond_tile == GOAL:
            new_grid[beyond_r][beyond_c] = BOX_ON_GOAL
        else:
            new_grid[beyond_r][beyond_c] = BOX

    # 7. Place the pusher in the target cell
    #    A goal exists under target if original tile was GOAL, BOX_ON_GOAL
    if target_tile in (GOAL, BOX_ON_GOAL):
        new_grid[target_r][target_c] = PUSHER_ON_GOAL
    else:
        new_grid[target_r][target_c] = PUSHER

    return new_grid


def is_solved(grid: list[list[str]]) -> bool:
    """
    Return True when every box is on a goal.
    i.e., there are NO bare '$' tiles left on the board.
    """
    return not any(BOX in row for row in grid)


# ─────────────────────────────────────────────
# 5.  INPUT  (simple WASD via input())
# ─────────────────────────────────────────────

def get_keypress() -> str | None:
    """
    Read one keypress and map it to 'U', 'D', 'L', 'R', or 'Q' (quit).
    Returns None for unrecognised keys.
    Uses simple input() — type w/a/s/d to move, q to quit, then press Enter.
    """
    key = input("Move (w/a/s/d) or q to quit: ").strip().lower()
    return {'w': 'U', 'a': 'L', 's': 'D', 'd': 'R', 'q': 'Q'}.get(key)


# ─────────────────────────────────────────────
# 6.  TASK A — MANUAL PLAY LOOP
# ─────────────────────────────────────────────

def play(raw_string: str):
    """
    Load the level and let the player solve it interactively.
    Press Q to quit at any time.
    """
    grid = parse_level(raw_string)
    render(grid)
    print("Controls: W/A/S/D or Arrow Keys   |   Q to quit")

    while True:
        key = get_keypress()

        if key == 'Q':
            print("Quitting.")
            break

        if key in DIRECTIONS:
            new_grid = apply_move(grid, key)
            if new_grid is not None:
                grid = new_grid

        render(grid)

        if is_solved(grid):
            print("Level Clear!")
            break


# ─────────────────────────────────────────────
# 7.  TASK B — BFS SOLVER
# ─────────────────────────────────────────────

def grid_to_state(grid: list[list[str]]) -> tuple:
    """
    Convert the grid into a hashable state for the BFS visited set.

    State = (pusher_pos, frozenset_of_box_positions)

    We don't need to encode walls or goals in the state because they
    never change — only the pusher and boxes move.
    """
    pusher_pos, box_positions, _ = find_positions(grid)
    return (pusher_pos, box_positions)


def bfs_solve(raw_string: str) -> str | None:
    """
    Run BFS over the Sokoban state space.
    Returns the LURD solution string, or None if unsolvable.

    BFS skeleton:
    ─────────────
    queue  : deque of (grid, lurd_string_so_far)
    visited: set of states  (use grid_to_state)

    Each iteration:
        pop (grid, path) from the LEFT of the queue
        for each direction in DIRECTIONS:
            new_grid = apply_move(grid, direction)
            if new_grid is None → skip
            if is_solved(new_grid) → return path + direction
            state = grid_to_state(new_grid)
            if state not in visited:
                visited.add(state)
                queue.append((new_grid, path + direction))

    TODO: fill in the loop body below.
    """
    initial_grid = parse_level(raw_string)
    initial_state = grid_to_state(initial_grid)

    queue   = deque([(initial_grid, "")])
    visited = {initial_state}

    while queue:
        grid, path = queue.popleft()

        for direction in DIRECTIONS:
            # TODO: apply move, check solved, enqueue if unseen
            pass

    return None  # no solution found


# ─────────────────────────────────────────────
# 8.  TASK B — PLAYBACK ENGINE
# ─────────────────────────────────────────────

def playback(raw_string: str, lurd: str, delay: float = 0.3):
    """
    Given a solution string, replay it step by step in the terminal.

    Steps:
    1. Print the LURD string.
    2. Reset to the initial grid.
    3. For each move in lurd:
           apply it, render, sleep(delay).
    4. Print "Level Clear!" at the end.
    """
    print(f"Solution: {lurd}\n")
    time.sleep(1)

    grid = parse_level(raw_string)
    render(grid)
    time.sleep(delay)

    for move in lurd:
        new_grid = apply_move(grid, move)
        if new_grid is not None:
            grid = new_grid
        render(grid)
        time.sleep(delay)

    print("Level Clear!")


# ─────────────────────────────────────────────
# 9.  ENTRY POINT
# ─────────────────────────────────────────────

# Paste Example 2's raw string here once you work it out:
EXAMPLE_2 = "11:####       ###### #   # #        # .#       #@  #########        ## #  #  # ##   $     ##   #####  #####      "

mode = input("Mode? [play / solve]: ").strip().lower()
level = input("Paste raw string: ").strip()

if mode == "play":
    play(level)
elif mode == "solve":
    print("Running BFS solver...")
    solution = bfs_solve(level)
    if solution:
        playback(level, solution)
    else:
        print("No solution found")
else:
    print("Invalid Input")
