from __future__ import annotations

import random
import unittest

from maze_escape.algorithms import astar, bfs_distances, generate_maze, raycast_fov
from maze_escape.settings import COLS, ROWS


class TestAlgorithms(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = random.Random(2026)
        self.maze = generate_maze(COLS, ROWS, self.rng)
        self.start = (1, 1)

    def test_generate_maze_creates_connected_graph(self) -> None:
        distances = bfs_distances(self.maze, self.start)
        self.assertEqual(len(distances), len(self.maze.floors))

    def test_astar_finds_path_to_farthest_cell(self) -> None:
        distances = bfs_distances(self.maze, self.start)
        goal = max(distances, key=distances.get)
        path = astar(self.maze, self.start, goal)

        self.assertTrue(path)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], goal)
        self.assertTrue(all(self.maze.passable(cell) for cell in path))

    def test_raycast_fov_shows_nearby_cells(self) -> None:
        visible = raycast_fov(self.maze, self.start)
        self.assertIn(self.start, visible)
        self.assertGreater(len(visible), 1)


if __name__ == "__main__":
    unittest.main()
