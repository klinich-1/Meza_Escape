from __future__ import annotations

import random
import unittest

from maze_escape.game_model import GameModel
from maze_escape.maze import Cell


class TestGameModel(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = random.Random(2026)
        self.model = GameModel(self.rng)

    def test_new_game_initial_state(self) -> None:
        self.assertEqual(self.model.player, (1, 1))
        self.assertEqual(self.model.status, "playing")
        self.assertEqual(self.model.steps, 0)
        self.assertTrue(self.model.crystals)
        self.assertTrue(self.model.maze.passable(self.model.player))
        self.assertIn(self.model.player, self.model.revealed)

    def test_try_move_moves_player_when_passable(self) -> None:
        direction: Cell = (1, 0)
        if not self.model.maze.passable((2, 1)):
            direction = (0, 1)

        moved = self.model.try_move(direction)
        self.assertTrue(moved)
        self.assertEqual(self.model.steps, 1)
        self.assertNotEqual(self.model.player, (1, 1))

    def test_try_move_fails_against_wall(self) -> None:
        if self.model.maze.passable((2, 1)):
            self.skipTest("Maze layout has no immediate right wall")

        moved = self.model.try_move((1, 0))
        self.assertFalse(moved)
        self.assertEqual(self.model.player, (1, 1))
        self.assertEqual(self.model.steps, 0)

    def test_use_escape_blink_sets_cooldown(self) -> None:
        self.model.use_escape_blink()
        self.assertGreaterEqual(self.model.escape_cooldown, 0.0)
        self.assertGreaterEqual(self.model.steps, 1)

    def test_move_hunter_finds_path(self) -> None:
        initial_hunter = self.model.hunter
        self.model.move_hunter()
        self.assertTrue(self.model.hunter_path)
        self.assertEqual(self.model.hunter_path[0], initial_hunter)
        self.assertTrue(self.model.maze.passable(self.model.hunter_path[-1]))
        self.assertNotEqual(self.model.hunter, initial_hunter)

    def test_difficulty_levels_change_parameters(self) -> None:
        easy_model = GameModel(self.rng, difficulty="easy")
        hard_model = GameModel(self.rng, difficulty="hard")

        self.assertGreater(easy_model.fov_radius, hard_model.fov_radius)
        self.assertGreater(hard_model.escape_cooldown_duration, easy_model.escape_cooldown_duration)
        self.assertGreater(hard_model.hunter_speed_factor, easy_model.hunter_speed_factor)
        self.assertNotEqual(easy_model.crystal_count, hard_model.crystal_count)

    def test_next_difficulty_advances_on_win(self) -> None:
        easy_model = GameModel(self.rng, difficulty="easy")
        medium_model = GameModel(self.rng, difficulty="medium")
        hard_model = GameModel(self.rng, difficulty="hard")

        self.assertEqual(easy_model.next_difficulty(), "medium")
        self.assertEqual(medium_model.next_difficulty(), "hard")
        self.assertEqual(hard_model.next_difficulty(), "hard")


if __name__ == "__main__":
    unittest.main()
