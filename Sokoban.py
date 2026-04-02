import time


WALL = '#'
PUSHER = '@'
PUSHER_ON_GOAL = '+'
BOX = '$'
BOX_ON_GOAL = '*'
GOAL = '.'
FLOOR = ' '
DIRECTIONS = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1),
}

def parse_level(raw_string):
    colon_idx = raw_string.index(':')
    width = int(raw_string[:colon_idx])
    data  = raw_string[colon_idx + 1:]

    grid = []
    for i in range(0, len(data), width):
        grid.append(list(data[i:i + width]))
    return grid


def find_positions(grid):
    pusher_pos    = None
    box_positions = set()
    goal_positions = set()

    for r in range(len(grid)):
        for c in range(len(grid[r])):
            tile = grid[r][c]
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




def render(grid):
    print('\n' * 50)
    for row in grid:
        print(''.join(row))
    print()  


def is_walkable(tile):
    return tile in (FLOOR, GOAL)


def is_box(tile):
    return tile in (BOX, BOX_ON_GOAL)


def apply_move(grid, direction):

    pusher_r, pusher_c = None, None
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] in (PUSHER, PUSHER_ON_GOAL):
                pusher_r, pusher_c = r, c
                break
        if pusher_r is not None:
            break

    dr, dc = DIRECTIONS[direction]
    target_r, target_c = pusher_r + dr, pusher_c + dc
    target_tile = grid[target_r][target_c]

    if target_tile == WALL:
        return None

    if is_box(target_tile):
        beyond_r, beyond_c = target_r + dr, target_c + dc
        beyond_tile = grid[beyond_r][beyond_c]
        if not is_walkable(beyond_tile):
            return None
    else:
        if not is_walkable(target_tile):
            return None

    new_grid = [row[:] for row in grid]

    if grid[pusher_r][pusher_c] == PUSHER_ON_GOAL:
        new_grid[pusher_r][pusher_c] = GOAL
    else:
        new_grid[pusher_r][pusher_c] = FLOOR

    if is_box(target_tile):
        beyond_r, beyond_c = target_r + dr, target_c + dc
        beyond_tile = grid[beyond_r][beyond_c]
        if beyond_tile == GOAL:
            new_grid[beyond_r][beyond_c] = BOX_ON_GOAL
        else:
            new_grid[beyond_r][beyond_c] = BOX

    if target_tile in (GOAL, BOX_ON_GOAL):
        new_grid[target_r][target_c] = PUSHER_ON_GOAL
    else:
        new_grid[target_r][target_c] = PUSHER

    return new_grid


def get_keypress():
    key = input("Move (w/a/s/d) or q to quit: ").strip().lower()
    return {'w': 'U', 'a': 'L', 's': 'D', 'd': 'R', 'q': 'Q'}.get(key)


def play(raw_string):
    grid = parse_level(raw_string)
    render(grid)
    print("Controls: W/A/S/D or Arrow Keys or Q to quit")

    while True:
        key = get_keypress()

        if key == 'Q':
            print("Quitting...")
            break

        if key in DIRECTIONS:
            new_grid = apply_move(grid, key)
            if new_grid is not None:
                grid = new_grid

        render(grid)

        solved = True
        for row in grid:
            if BOX in row:
                solved = False
                break
        if solved:
            print("Level Clear!")
            break


def grid_to_state(grid):
    pusher_pos, box_positions, _ = find_positions(grid)
    return (pusher_pos, box_positions)


def bfs_solve(raw_string):
    initial_grid = parse_level(raw_string)
    initial_state = grid_to_state(initial_grid)

    queue   = [(initial_grid, "")]
    visited = {initial_state}

    while queue:
        grid, path = queue.pop(0)

        for direction in DIRECTIONS:
            new_grid = apply_move(grid, direction)
            if new_grid is None:
                continue
            solved = True
            for row in new_grid:
                if BOX in row:
                    solved = False
                    break
            if solved:
                return path + direction

            state = grid_to_state(new_grid)
            if state not in visited:
                visited.add(state)
                queue.append((new_grid, path + direction))

    return None


def playback(raw_string, lurd):
    print(f"Solution: {lurd}\n")
    time.sleep(1)

    grid = parse_level(raw_string)
    render(grid)
    time.sleep(1)

    for move in lurd:
        new_grid = apply_move(grid, move)
        if new_grid is not None:
            grid = new_grid
        render(grid)
        time.sleep(1)

    print(f"Solution: {lurd}\n")
    print("Level Clear!")



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