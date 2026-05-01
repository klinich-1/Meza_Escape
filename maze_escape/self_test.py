from __future__ import annotations

import random

from maze_escape.algorithms import astar, bfs_distances, generate_maze, raycast_fov
from maze_escape.settings import COLS, ROWS


def run_self_test() -> int:
    rng = random.Random(2026)
    maze = generate_maze(COLS, ROWS, rng)
    start = (1, 1)
    distances = bfs_distances(maze, start)

    assert len(distances) == len(maze.floors), "maze must be fully connected"

    goal = max(distances, key=distances.get)
    path = astar(maze, start, goal)
    assert path[0] == start and path[-1] == goal, "A* must reach the farthest cell"
    assert all(maze.passable(cell) for cell in path), "A* path must avoid walls"

    visible = raycast_fov(maze, start)
    assert start in visible, "FOV must include the player cell"
    assert len(visible) > 1, "FOV must reveal nearby cells"

    print(
        "Self-test OK: "
        f"floors={len(maze.floors)}, path_length={len(path)}, "
        f"visible_cells={len(visible)}"
    )
    return 0
# Тесты

# Добавлены дополнительные проверки самотестирования

# Проверка корректности вычисления видимости
