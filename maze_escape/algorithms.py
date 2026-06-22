from __future__ import annotations

import heapq
import math
import random
from collections import deque
from typing import Dict, Iterable, List, Optional, Set, Tuple

from maze_escape.maze import Cell, Maze
from maze_escape.settings import FOV_RADIUS, FOV_RAYS


def neighbors4(cell: Cell) -> Iterable[Cell]:
    x, y = cell
    yield x + 1, y
    yield x - 1, y
    yield x, y + 1
    yield x, y - 1


def generate_maze(cols: int, rows: int, rng: random.Random, extra_passages: Optional[int] = None) -> Maze:
    grid = [[True for _ in range(cols)] for _ in range(rows)]
    start = (1, 1)
    grid[start[1]][start[0]] = False
    stack = [start]
    visited = {start}
    directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]

    while stack:
        x, y = stack[-1]
        options: List[Tuple[int, int, int, int]] = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < cols - 1 and 1 <= ny < rows - 1:
                if (nx, ny) not in visited:
                    options.append((nx, ny, dx, dy))

        if not options:
            stack.pop()
            continue

        nx, ny, dx, dy = rng.choice(options)
        grid[y + dy // 2][x + dx // 2] = False
        grid[ny][nx] = False
        visited.add((nx, ny))
        stack.append((nx, ny))

    if extra_passages is None:
        extra_passages = cols * rows // 26

    _add_extra_passages(grid, rng, extra_passages)
    return _grid_to_maze(grid, cols, rows)


def bfs_distances(maze: Maze, start: Cell) -> Dict[Cell, int]:
    queue = deque([start])
    distances = {start: 0}

    while queue:
        current = queue.popleft()
        for nxt in neighbors4(current):
            if nxt not in distances and maze.passable(nxt):
                distances[nxt] = distances[current] + 1
                queue.append(nxt)

    return distances


def astar(maze: Maze, start: Cell, goal: Cell) -> List[Cell]:
    if start == goal:
        return [start]

    frontier: List[Tuple[int, int, Cell]] = []
    heapq.heappush(frontier, (0, 0, start))
    came_from: Dict[Cell, Optional[Cell]] = {start: None}
    cost_so_far: Dict[Cell, int] = {start: 0}
    counter = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for nxt in neighbors4(current):
            if not maze.passable(nxt):
                continue

            new_cost = cost_so_far[current] + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                counter += 1
                priority = new_cost + _manhattan(nxt, goal)
                heapq.heappush(frontier, (priority, counter, nxt))
                came_from[nxt] = current

    if goal not in came_from:
        return []

    return _reconstruct_path(came_from, start, goal)


def raycast_fov(
    maze: Maze,
    origin: Cell,
    radius: int = FOV_RADIUS,
    ray_count: int = FOV_RAYS,
) -> Set[Cell]:
    visible = {origin}
    ox = origin[0] + 0.5
    oy = origin[1] + 0.5
    step_size = 0.08
    max_steps = int(radius / step_size)

    for i in range(ray_count):
        angle = 2.0 * math.pi * i / ray_count
        dx = math.cos(angle) * step_size
        dy = math.sin(angle) * step_size
        x = ox
        y = oy

        for _ in range(max_steps):
            x += dx
            y += dy
            cell = (int(x), int(y))

            if not maze.in_bounds(cell):
                break

            visible.add(cell)
            if cell in maze.walls:
                break

    return visible


def _add_extra_passages(
    grid: List[List[bool]],
    rng: random.Random,
    openings: int,
) -> None:
    candidates: List[Cell] = []
    rows = len(grid)
    cols = len(grid[0])

    for y in range(1, rows - 1):
        for x in range(1, cols - 1):
            if not grid[y][x]:
                continue

            horizontal_link = not grid[y][x - 1] and not grid[y][x + 1]
            vertical_link = not grid[y - 1][x] and not grid[y + 1][x]
            if horizontal_link or vertical_link:
                candidates.append((x, y))

    rng.shuffle(candidates)
    for x, y in candidates[:openings]:
        grid[y][x] = False


def _grid_to_maze(grid: List[List[bool]], cols: int, rows: int) -> Maze:
    walls: Set[Cell] = set()
    floors: Set[Cell] = set()

    for y in range(rows):
        for x in range(cols):
            if grid[y][x]:
                walls.add((x, y))
            else:
                floors.add((x, y))

    return Maze(walls=walls, floors=floors, cols=cols, rows=rows)


def _manhattan(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _reconstruct_path(
    came_from: Dict[Cell, Optional[Cell]],
    start: Cell,
    goal: Cell,
) -> List[Cell]:
    path = [goal]
    while path[-1] != start:
        previous = came_from[path[-1]]
        if previous is None:
            break
        path.append(previous)

    path.reverse()
    return path
