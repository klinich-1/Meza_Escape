from __future__ import annotations

import random
from typing import Optional

import maze_escape.settings as settings
from maze_escape.maze import Cell
from maze_escape.game_model import GameModel


class Game:
    def __init__(self, pygame_module) -> None:
        self.pg = pygame_module
        self.screen = self.pg.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.pg.display.set_icon(self.create_window_icon())
        self.pg.display.set_caption("Maze Escape")
        self.clock = self.pg.time.Clock()
        self.font = self.pg.font.Font(None, settings.FONT_TITLE_SIZE)
        self.small_font = self.pg.font.Font(None, settings.FONT_MENU_SIZE)
        self.running = True
        self.rng = random.Random()
        self.model = GameModel(self.rng)
        # UI state: 'menu' or 'playing'
        self.ui_state = "menu"
        self.menu_options = [
            settings.DIFFICULTY_LABELS["easy"],
            settings.DIFFICULTY_LABELS["medium"],
            settings.DIFFICULTY_LABELS["hard"],
            "Выход",
        ]
        self.difficulty_values = ["easy", "medium", "hard"]
        self.menu_selected = 0
        self.pause_options = ["Продолжить", "В меню"]

    def create_window_icon(self):
        icon = self.pg.Surface((32, 32), self.pg.SRCALPHA)
        icon.fill((16, 23, 33, 255))

        wall = (29, 42, 58)
        path = (84, 190, 112)
        player = (91, 176, 214)

        self.pg.draw.rect(icon, wall, (0, 0, 32, 4))
        self.pg.draw.rect(icon, wall, (0, 28, 32, 4))
        self.pg.draw.rect(icon, wall, (0, 0, 4, 32))
        self.pg.draw.rect(icon, wall, (28, 0, 4, 32))

        self.pg.draw.rect(icon, wall, (8, 8, 16, 4))
        self.pg.draw.rect(icon, wall, (8, 20, 16, 4))
        self.pg.draw.rect(icon, path, (12, 12, 8, 8))
        self.pg.draw.circle(icon, player, (16, 16), 4)

        return icon

    @property
    def collected(self) -> int:
        return self.model.collected

    def run(self) -> None:
        while self.running:
            # Цикл игры обновляет состояние и перерисовывает кадр
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
                elif self.ui_state == "menu":
                    if event.key in (self.pg.K_UP, self.pg.K_w):
                        self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
                    elif event.key in (self.pg.K_DOWN, self.pg.K_s):
                        self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
                    elif event.key in (self.pg.K_RETURN, self.pg.K_SPACE):
                        if self.menu_selected < len(self.difficulty_values):
                            difficulty = self.difficulty_values[self.menu_selected]
                            self.model.new_game(difficulty)
                            self.ui_state = "playing"
                        else:
                            self.running = False
                elif self.ui_state == "paused":
                    if event.key in (self.pg.K_UP, self.pg.K_w):
                        self.menu_selected = (self.menu_selected - 1) % len(self.pause_options)
                    elif event.key in (self.pg.K_DOWN, self.pg.K_s):
                        self.menu_selected = (self.menu_selected + 1) % len(self.pause_options)
                    elif event.key in (self.pg.K_RETURN, self.pg.K_SPACE, self.pg.K_p):
                        if self.menu_selected == 0:
                            self.ui_state = "playing"
                        else:
                            self.ui_state = "menu"
                    elif event.key == self.pg.K_p:
                        # allow toggling pause with P
                        self.ui_state = "playing"
                elif event.key == self.pg.K_r:
                    self.model.new_game(self.model.difficulty)
                elif self.model.status == "playing":
                    if event.key == self.pg.K_p:
                        # toggle pause
                        self.ui_state = "paused"
                        # reset pause menu selection
                        self.menu_selected = 0
                    elif event.key == self.pg.K_SPACE:
                        self.model.use_escape_blink()
                    else:
                        self.start_held_movement(event.key)
                elif event.key in (self.pg.K_RETURN, self.pg.K_SPACE):
                    # restart after win/lose
                    next_difficulty = self.model.next_difficulty() if self.model.status == "won" else self.model.difficulty
                    self.model.new_game(next_difficulty)
                    self.ui_state = "playing"

    def start_held_movement(self, key: int) -> None:
        direction = self.direction_for_key(key)
        if direction is None:
            return

        self.model.held_direction = direction
        self.model.try_move(direction)
        self.model.move_timer = settings.PLAYER_MOVE_DELAY

    def update_held_movement(self, dt: float) -> None:
        self.model.move_timer = max(0.0, self.model.move_timer - dt)
        direction = self.current_held_direction()

        if direction is None:
            self.model.held_direction = None
            return

        if self.model.move_timer <= 0:
            self.model.held_direction = direction
            self.model.try_move(direction)
            self.model.move_timer = settings.PLAYER_MOVE_DELAY

    def current_held_direction(self) -> Optional[Cell]:
        keys = self.pg.key.get_pressed()
        if self.model.held_direction is not None:
            for key in self.keys_for_direction(self.model.held_direction):
                if keys[key]:
                    return self.model.held_direction

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

    def update(self, dt: float) -> None:
        # Only update game logic while actively playing (not in menu/pause)
        if self.ui_state != "playing":
            return

        if self.model.status != "playing":
            return

        self.model.update(dt)
        self.update_held_movement(dt)

    def draw(self) -> None:
        self.screen.fill((7, 10, 18))

        if self.ui_state == "menu":
            self.draw_menu()
            self.pg.display.flip()
            return

        self.draw_hud()
        self.draw_maze()
        self.draw_path_hint()
        self.draw_entities()

        if self.ui_state == "paused":
            self.draw_pause()
        elif self.model.status != "playing":
            self.draw_overlay()

        self.pg.display.flip()

    def draw_hud(self) -> None:
        self.draw_hud_background()

        title = self.font.render("Maze Escape", True, (239, 241, 225))
        self.screen.blit(title, (18, 19))

        self.draw_stat_card(
            settings.SCREEN_WIDTH - 322,
            (246, 207, 94),
            f"{self.collected}/{self.model.crystal_count}",
            "crystal",
        )
        self.draw_stat_card(
            settings.SCREEN_WIDTH - 214,
            (98, 176, 214),
            str(self.model.steps),
            "steps",
        )
        self.draw_stat_card(
            settings.SCREEN_WIDTH - 106,
            (102, 214, 147),
            self.blink_label(),
            "blink",
        )
        difficulty = settings.DIFFICULTY_LABELS.get(self.model.difficulty, "Средне")
        diff_text = self.small_font.render(f"Сложность: {difficulty}", True, (150, 150, 150))
        self.screen.blit(diff_text, (18, 50))

    def draw_hud_background(self) -> None:
        top = (9, 12, 22)
        bottom = (19, 24, 37)
        for y in range(settings.HUD_HEIGHT):
            factor = y / max(1, settings.HUD_HEIGHT - 1)
            color = tuple(
                int(top[i] + (bottom[i] - top[i]) * factor)
                for i in range(3)
            )
            self.pg.draw.line(self.screen, color, (0, y), (settings.SCREEN_WIDTH, y))

        self.pg.draw.line(
            self.screen,
            (48, 66, 82),
            (0, settings.HUD_HEIGHT - 1),
            (settings.SCREEN_WIDTH, settings.HUD_HEIGHT - 1),
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
        if self.model.escape_cooldown <= 0:
            return "OK"
        return f"{self.model.escape_cooldown:.1f}s"

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
        for y in range(settings.ROWS):
            for x in range(settings.COLS):
                cell = (x, y)
                rect = self.cell_rect(cell)

                if cell not in self.model.revealed:
                    color = (5, 7, 12)
                elif cell in self.model.maze.walls:
                    color = (29, 42, 58) if cell in self.model.visible else (16, 23, 33)
                else:
                    color = (36, 45, 43) if cell in self.model.visible else (20, 27, 28)

                self.pg.draw.rect(self.screen, color, rect)

        exit_color = (84, 190, 112) if not self.model.crystals else (142, 77, 62)
        if self.model.exit_cell in self.model.revealed:
            self.pg.draw.rect(
                self.screen,
                exit_color,
                self.cell_rect(self.model.exit_cell).inflate(-8, -8),
                border_radius=4,
            )

        for crystal in self.model.crystals:
            if crystal in self.model.visible:
                cx, cy = self.cell_center(crystal)
                self.pg.draw.circle(self.screen, (246, 207, 94), (cx, cy), 7)
                self.pg.draw.circle(self.screen, (255, 246, 172), (cx - 2, cy - 2), 3)

    def draw_path_hint(self) -> None:
        if self.model.status != "playing":
            return

        for cell in self.model.hunter_path[1:10]:
            if cell not in self.model.revealed or cell in self.model.maze.walls:
                continue
            cx, cy = self.cell_center(cell)
            self.pg.draw.circle(self.screen, (122, 55, 64), (cx, cy), 3)

    def draw_entities(self) -> None:
        px, py = self.cell_center(self.model.player)
        self.pg.draw.circle(self.screen, (91, 176, 214), (px, py), 10)
        self.pg.draw.circle(self.screen, (202, 244, 255), (px - 3, py - 3), 4)

        if self.model.hunter in self.model.visible:
            hx, hy = self.cell_center(self.model.hunter)
            self.pg.draw.circle(self.screen, (216, 72, 82), (hx, hy), 10)
            self.pg.draw.circle(self.screen, (255, 168, 142), (hx - 3, hy - 3), 4)

    def draw_overlay(self) -> None:
        overlay = self.pg.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), self.pg.SRCALPHA)
        overlay.fill((3, 5, 9, 178))
        self.screen.blit(overlay, (0, 0))

        text = self.font.render(self.model.message, True, (245, 240, 220))
        rect = text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        self.pg.draw.rect(
            self.screen,
            (28, 34, 43),
            rect.inflate(44, 28),
            border_radius=8,
        )
        self.screen.blit(text, rect)

    def draw_menu(self) -> None:
        title = self.font.render("Maze Escape", True, (239, 241, 225))
        title_rect = title.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3 - 40))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render("Выберите уровень сложности:", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3 + 20))
        self.screen.blit(subtitle, subtitle_rect)

        for i, option in enumerate(self.menu_options):
            is_selected = i == self.menu_selected
            color = (246, 207, 94) if is_selected else (200, 200, 200)
            
            if is_selected:
                opt_text = self.small_font.render(f"  > {option} <  ", True, color)
            else:
                opt_text = self.small_font.render(f"    {option}    ", True, color)
            
            rect = opt_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + i * 50))
            
            if is_selected:
                box = self.pg.Rect(rect.x - 5, rect.y - 5, rect.width + 10, rect.height + 10)
                self.pg.draw.rect(self.screen, (246, 207, 94), box, 2)
            
            self.screen.blit(opt_text, rect)

    def draw_pause(self) -> None:
        overlay = self.pg.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), self.pg.SRCALPHA)
        overlay.fill((3, 5, 9, 178))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("Пауза", True, (239, 241, 225))
        title_rect = title.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)

        for i, option in enumerate(self.pause_options):
            is_selected = i == self.menu_selected
            color = (246, 207, 94) if is_selected else (200, 200, 200)
            
            if is_selected:
                opt_text = self.small_font.render(f"  > {option} <  ", True, color)
            else:
                opt_text = self.small_font.render(f"    {option}    ", True, color)
            
            rect = opt_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + i * 50))
            
            if is_selected:
                box = self.pg.Rect(rect.x - 5, rect.y - 5, rect.width + 10, rect.height + 10)
                self.pg.draw.rect(self.screen, (246, 207, 94), box, 2)
            
            self.screen.blit(opt_text, rect)

    def cell_rect(self, cell: Cell):
        x, y = cell
        return self.pg.Rect(x * settings.TILE, settings.HUD_HEIGHT + y * settings.TILE, settings.TILE, settings.TILE)

    def cell_center(self, cell: Cell) -> Cell:
        x, y = cell
        return x * settings.TILE + settings.TILE // 2, settings.HUD_HEIGHT + y * settings.TILE + settings.TILE // 2
