from __future__ import annotations

import random
from collections import deque
from typing import List, Optional

from maze_escape.algorithms import astar, bfs_distances, generate_maze, raycast_fov
from maze_escape.maze import Cell
from maze_escape.settings import (
    COLS,
    DIFFICULTY_CONFIGS,
    DIFFICULTY_LEVELS,
    HUNTER_STUN_AFTER_BLINK,
    ROWS,
)


class GameModel:
    def __init__(self, rng: Optional[random.Random] = None, difficulty: str = "medium") -> None:
        self.rng = rng or random.Random()
        self.difficulty = difficulty
        self.new_game(difficulty)

    def new_game(self, difficulty: str = "medium") -> None:
        difficulty = difficulty.lower()
        if difficulty not in DIFFICULTY_LEVELS:
            difficulty = "medium"
        self.difficulty = difficulty
        config = DIFFICULTY_CONFIGS[difficulty]

        self.maze = generate_maze(
            COLS,
            ROWS,
            self.rng,
            extra_passages=int(COLS * ROWS * config["extra_passages_factor"]),
        )
        self.player = (1, 1)
        distances = bfs_distances(self.maze, self.player)
        farthest = max(distances, key=distances.get)
        self.exit_cell = farthest

        blocked = {self.player, self.exit_cell}
        hunter_candidates = sorted(
            (cell for cell in distances if cell not in blocked),
            key=lambda cell: distances[cell],
            reverse=True,
        )
        self.hunter = hunter_candidates[min(4, len(hunter_candidates) - 1)]
        blocked.add(self.hunter)

        crystal_candidates = [
            cell
            for cell, distance in distances.items()
            if cell not in blocked and distance > max(8, distances[farthest] // 4)
        ]
        self.rng.shuffle(crystal_candidates)
        self.crystal_count = config["crystal_count"]
        self.crystals = set(crystal_candidates[: self.crystal_count])

        self.fov_radius = config["fov_radius"]
        self.escape_blink_range = config["escape_blink_range"]
        self.escape_cooldown_duration = config["escape_cooldown"]
        self.hunter_speed_factor = config["hunter_speed_factor"]

        self.visible = raycast_fov(self.maze, self.player, radius=self.fov_radius)
        self.revealed = set(self.visible)
        self.hunter_path: List[Cell] = []
        self.enemy_timer = 0.0
        self.move_timer = 0.0
        self.held_direction: Optional[Cell] = None
        self.escape_cooldown = 0.0
        self.hunter_stun = 0.0
        self.steps = 0
        self.status = "playing"
        self.message = ""

    @property
    def collected(self) -> int:
        return self.crystal_count - len(self.crystals)

    def try_move(self, direction: Cell) -> bool:
        dx, dy = direction
        target = (self.player[0] + dx, self.player[1] + dy)
        if not self.maze.passable(target):
            return False

        self.player = target
        self.steps += 1
        self.visible = raycast_fov(self.maze, self.player, radius=self.fov_radius)
        self.revealed.update(self.visible)
        self.collect_current_cell()
        self.check_end_conditions()
        return True

    def use_escape_blink(self) -> None:
        if self.escape_cooldown > 0:
            return

        target = self.find_escape_blink_target()
        if target == self.player:
            return

        self.player = target
        self.steps += 1
        self.escape_cooldown = self.escape_cooldown_duration
        self.hunter_stun = HUNTER_STUN_AFTER_BLINK
        self.enemy_timer = 0.0
        self.hunter_path = []
        self.visible = raycast_fov(self.maze, self.player, radius=self.fov_radius)
        self.revealed.update(self.visible)
        self.collect_current_cell()
        self.check_end_conditions()

    def find_escape_blink_target(self) -> Cell:
        local_distances = self.reachable_cells_near_player(self.escape_blink_range)
        hunter_distances = bfs_distances(self.maze, self.hunter)

        candidates = [
            cell
            for cell in local_distances
            if cell != self.player and cell != self.hunter
        ]
        if not candidates:
            return self.player

        return max(
            candidates,
            key=lambda cell: (
                hunter_distances.get(cell, -1),
                local_distances[cell],
                self.rng.random(),
            ),
        )

    def reachable_cells_near_player(self, max_distance: int) -> dict[Cell, int]:
        queue = deque([self.player])
        distances = {self.player: 0}

        while queue:
            current = queue.popleft()
            if distances[current] >= max_distance:
                continue

            x, y = current
            for nxt in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if nxt in distances or not self.maze.passable(nxt):
                    continue
                distances[nxt] = distances[current] + 1
                queue.append(nxt)

        return distances

    def collect_current_cell(self) -> None:
        if self.player in self.crystals:
            self.crystals.remove(self.player)

    def update(self, dt: float) -> None:
        if self.status != "playing":
            return

        self.escape_cooldown = max(0.0, self.escape_cooldown - dt)
        self.hunter_stun = max(0.0, self.hunter_stun - dt)
        # held movement timers are managed by the app input loop (move_timer / held_direction)

        self.enemy_timer += dt
        delay = max(0.12, (0.46 - self.collected * 0.03) / self.hunter_speed_factor)

        if self.hunter_stun <= 0 and self.enemy_timer >= delay:
            self.enemy_timer = 0.0
            self.move_hunter()
            self.check_end_conditions()

    def move_hunter(self) -> None:
        self.hunter_path = astar(self.maze, self.hunter, self.player)
        if len(self.hunter_path) > 1:
            self.hunter = self.hunter_path[1]

    def next_difficulty(self) -> str:
        if self.difficulty == "easy":
            return "medium"
        if self.difficulty == "medium":
            return "hard"
        return "hard"

    def check_end_conditions(self) -> None:
        if self.hunter == self.player:
            self.status = "lost"
            self.message = "Пойман! Нажми Enter для перезагрузки."
        elif self.player == self.exit_cell and not self.crystals:
            self.status = "won"
            self.message = "Спасен! Нажми Enter для новой игры."
