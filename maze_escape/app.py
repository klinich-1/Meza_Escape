from __future__ import annotations

import random
from collections import deque
from typing import List, Optional

from maze_escape.algorithms import astar, bfs_distances, generate_maze, raycast_fov
from maze_escape.maze import Cell
from maze_escape.settings import (
    COLS,
    CRYSTAL_COUNT,
    ESCAPE_BLINK_RANGE,
    ESCAPE_COOLDOWN,
    HUNTER_STUN_AFTER_BLINK,
    HUD_HEIGHT,
    PLAYER_MOVE_DELAY,
    ROWS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE,
)


class Game:
    def __init__(self, pygame_module) -> None:
        self.pg = pygame_module
        self.screen = self.pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.pg.display.set_caption("Maze Escape")
        self.clock = self.pg.time.Clock()
        self.font = self.pg.font.Font(None, 32)
        self.small_font = self.pg.font.Font(None, 24)
        self.running = True
        self.rng = random.Random()
        self.new_game()

    def new_game(self) -> None:
        self.maze = generate_maze(COLS, ROWS, self.rng)
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
        self.crystals = set(crystal_candidates[:CRYSTAL_COUNT])

        self.visible = raycast_fov(self.maze, self.player)
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
        return CRYSTAL_COUNT - len(self.crystals)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        self.pg.quit()

    def handle_events(self) -> None:
        for event in self.pg.event.get():
            if event.type == self.pg.QUIT:
                self.running = False
            elif event.type == self.pg.KEYDOWN:
                if event.key == self.pg.K_ESCAPE:
                    self.running = False
                elif event.key == self.pg.K_r:
                    self.new_game()
                elif self.status == "playing":
                    if event.key == self.pg.K_SPACE:
                        self.use_escape_blink()
                    else:
                        self.start_held_movement(event.key)
                elif event.key in (self.pg.K_RETURN, self.pg.K_SPACE):
                    self.new_game()

    def start_held_movement(self, key: int) -> None:
        direction = self.direction_for_key(key)
        if direction is None:
            return

        self.held_direction = direction
        self.try_move(direction)
        self.move_timer = PLAYER_MOVE_DELAY

    def update_held_movement(self, dt: float) -> None:
        self.move_timer = max(0.0, self.move_timer - dt)
        direction = self.current_held_direction()

        if direction is None:
            self.held_direction = None
            return

        if self.move_timer <= 0:
            self.held_direction = direction
            self.try_move(direction)
            self.move_timer = PLAYER_MOVE_DELAY

    def current_held_direction(self) -> Optional[Cell]:
        keys = self.pg.key.get_pressed()

        if self.held_direction is not None:
            for key in self.keys_for_direction(self.held_direction):
                if keys[key]:
                    return self.held_direction

        for key in (
            self.pg.K_LEFT,
            self.pg.K_a,
            self.pg.K_RIGHT,
            self.pg.K_d,
            self.pg.K_UP,
            self.pg.K_w,
            self.pg.K_DOWN,
            self.pg.K_s,
        ):
            if keys[key]:
                return self.direction_for_key(key)

        return None

    def keys_for_direction(self, direction: Cell) -> tuple[int, int]:
        if direction == (-1, 0):
            return self.pg.K_LEFT, self.pg.K_a
        if direction == (1, 0):
            return self.pg.K_RIGHT, self.pg.K_d
        if direction == (0, -1):
            return self.pg.K_UP, self.pg.K_w
        return self.pg.K_DOWN, self.pg.K_s

    def direction_for_key(self, key: int) -> Optional[Cell]:
        movement = {
            self.pg.K_LEFT: (-1, 0),
            self.pg.K_a: (-1, 0),
            self.pg.K_RIGHT: (1, 0),
            self.pg.K_d: (1, 0),
            self.pg.K_UP: (0, -1),
            self.pg.K_w: (0, -1),
            self.pg.K_DOWN: (0, 1),
            self.pg.K_s: (0, 1),
        }
        return movement.get(key)

    def try_move(self, direction: Cell) -> bool:
        dx, dy = direction
        target = (self.player[0] + dx, self.player[1] + dy)
        if not self.maze.passable(target):
            return False

        self.player = target
        self.steps += 1
        self.visible = raycast_fov(self.maze, self.player)
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
        self.escape_cooldown = ESCAPE_COOLDOWN
        self.hunter_stun = HUNTER_STUN_AFTER_BLINK
        self.enemy_timer = 0.0
        self.hunter_path = []
        self.visible = raycast_fov(self.maze, self.player)
        self.revealed.update(self.visible)
        self.collect_current_cell()
        self.check_end_conditions()

    def find_escape_blink_target(self) -> Cell:
        local_distances = self.reachable_cells_near_player(ESCAPE_BLINK_RANGE)
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
        self.update_held_movement(dt)
        if self.status != "playing":
            return

        self.enemy_timer += dt
        delay = max(0.16, 0.46 - self.collected * 0.03)

        if self.hunter_stun <= 0 and self.enemy_timer >= delay:
            self.enemy_timer = 0.0
            self.move_hunter()
            self.check_end_conditions()

    def move_hunter(self) -> None:
        self.hunter_path = astar(self.maze, self.hunter, self.player)
        if len(self.hunter_path) > 1:
            self.hunter = self.hunter_path[1]

    def check_end_conditions(self) -> None:
        if self.hunter == self.player:
            self.status = "lost"
            self.message = "Caught. Press Enter to restart."
        elif self.player == self.exit_cell and not self.crystals:
            self.status = "won"
            self.message = "Escaped. Press Enter for a new maze."

    def draw(self) -> None:
        self.screen.fill((7, 10, 18))
        self.draw_hud()
        self.draw_maze()
        self.draw_path_hint()
        self.draw_entities()

        if self.status != "playing":
            self.draw_overlay()

        self.pg.display.flip()

    def draw_hud(self) -> None:
        self.draw_hud_background()

        title = self.font.render("Maze Escape", True, (239, 241, 225))
        self.screen.blit(title, (18, 19))
        self.pg.draw.rect(self.screen, (237, 195, 82), (18, 50, 104, 3), border_radius=2)

        self.draw_stat_card(
            SCREEN_WIDTH - 322,
            (246, 207, 94),
            f"{self.collected}/{CRYSTAL_COUNT}",
            "crystal",
        )
        self.draw_stat_card(
            SCREEN_WIDTH - 214,
            (98, 176, 214),
            str(self.steps),
            "steps",
        )
        self.draw_stat_card(
            SCREEN_WIDTH - 106,
            (102, 214, 147),
            self.blink_label(),
            "blink",
        )

    def draw_hud_background(self) -> None:
        top = (9, 12, 22)
        bottom = (19, 24, 37)
        for y in range(HUD_HEIGHT):
            factor = y / max(1, HUD_HEIGHT - 1)
            color = tuple(
                int(top[i] + (bottom[i] - top[i]) * factor)
                for i in range(3)
            )
            self.pg.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        self.pg.draw.line(
            self.screen,
            (48, 66, 82),
            (0, HUD_HEIGHT - 1),
            (SCREEN_WIDTH, HUD_HEIGHT - 1),
            2,
        )

    def draw_stat_card(self, x: int, color: tuple[int, int, int], value: str, icon: str) -> None:
        rect = self.pg.Rect(x, 17, 90, 40)
        self.pg.draw.rect(self.screen, (25, 31, 45), rect, border_radius=7)
        self.pg.draw.rect(self.screen, (48, 60, 76), rect, 1, border_radius=7)

        icon_center = (x + 19, 37)
        if icon == "crystal":
            self.draw_crystal_icon(icon_center, color)
        elif icon == "steps":
            self.draw_steps_icon(icon_center, color)
        else:
            self.draw_blink_icon(icon_center, color)

        text = self.small_font.render(value, True, (226, 234, 226))
        text_rect = text.get_rect(midleft=(x + 38, 37))
        self.screen.blit(text, text_rect)

    def blink_label(self) -> str:
        if self.escape_cooldown <= 0:
            return "OK"
        return f"{self.escape_cooldown:.1f}s"

    def draw_crystal_icon(self, center: Cell, color: tuple[int, int, int]) -> None:
        x, y = center
        points = [(x, y - 10), (x + 8, y), (x, y + 10), (x - 8, y)]
        self.pg.draw.polygon(self.screen, color, points)
        self.pg.draw.polygon(self.screen, (255, 246, 172), [(x, y - 7), (x + 4, y), (x, y + 3)])

    def draw_steps_icon(self, center: Cell, color: tuple[int, int, int]) -> None:
        x, y = center
        self.pg.draw.circle(self.screen, color, (x - 4, y + 4), 5)
        self.pg.draw.circle(self.screen, color, (x + 5, y - 5), 5)
        self.pg.draw.circle(self.screen, (184, 225, 238), (x - 5, y + 2), 2)

    def draw_blink_icon(self, center: Cell, color: tuple[int, int, int]) -> None:
        x, y = center
        points = [(x + 1, y - 12), (x - 8, y + 2), (x, y + 1), (x - 3, y + 12), (x + 9, y - 2), (x + 1, y - 1)]
        self.pg.draw.polygon(self.screen, color, points)

    def draw_maze(self) -> None:
        for y in range(ROWS):
            for x in range(COLS):
                cell = (x, y)
                rect = self.cell_rect(cell)

                if cell not in self.revealed:
                    color = (5, 7, 12)
                elif cell in self.maze.walls:
                    color = (29, 42, 58) if cell in self.visible else (16, 23, 33)
                else:
                    color = (36, 45, 43) if cell in self.visible else (20, 27, 28)

                self.pg.draw.rect(self.screen, color, rect)

        exit_color = (84, 190, 112) if not self.crystals else (142, 77, 62)
        if self.exit_cell in self.revealed:
            self.pg.draw.rect(
                self.screen,
                exit_color,
                self.cell_rect(self.exit_cell).inflate(-8, -8),
                border_radius=4,
            )

        for crystal in self.crystals:
            if crystal in self.visible:
                cx, cy = self.cell_center(crystal)
                self.pg.draw.circle(self.screen, (246, 207, 94), (cx, cy), 7)
                self.pg.draw.circle(self.screen, (255, 246, 172), (cx - 2, cy - 2), 3)

    def draw_path_hint(self) -> None:
        if self.status != "playing":
            return

        for cell in self.hunter_path[1:10]:
            if cell not in self.revealed or cell in self.maze.walls:
                continue
            cx, cy = self.cell_center(cell)
            self.pg.draw.circle(self.screen, (122, 55, 64), (cx, cy), 3)

    def draw_entities(self) -> None:
        px, py = self.cell_center(self.player)
        self.pg.draw.circle(self.screen, (91, 176, 214), (px, py), 10)
        self.pg.draw.circle(self.screen, (202, 244, 255), (px - 3, py - 3), 4)

        if self.hunter in self.visible:
            hx, hy = self.cell_center(self.hunter)
            self.pg.draw.circle(self.screen, (216, 72, 82), (hx, hy), 10)
            self.pg.draw.circle(self.screen, (255, 168, 142), (hx - 3, hy - 3), 4)

    def draw_overlay(self) -> None:
        overlay = self.pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), self.pg.SRCALPHA)
        overlay.fill((3, 5, 9, 178))
        self.screen.blit(overlay, (0, 0))

        text = self.font.render(self.message, True, (245, 240, 220))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.pg.draw.rect(
            self.screen,
            (28, 34, 43),
            rect.inflate(44, 28),
            border_radius=8,
        )
        self.screen.blit(text, rect)

    def cell_rect(self, cell: Cell):
        x, y = cell
        return self.pg.Rect(x * TILE, HUD_HEIGHT + y * TILE, TILE, TILE)

    def cell_center(self, cell: Cell) -> Cell:
        x, y = cell
        return x * TILE + TILE // 2, HUD_HEIGHT + y * TILE + TILE // 2
# Улучшен интерфейс

# Улучшена читаемость игрового цикла

# Обновлена логика отрисовки интерфейса

# Инициализация игрового состояния
