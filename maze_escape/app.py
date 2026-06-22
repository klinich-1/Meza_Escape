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
        icon = self.pg.Surface((settings.ICON_SIZE, settings.ICON_SIZE), self.pg.SRCALPHA)
        icon.fill(settings.COLOR_ICON_BG)

        self.pg.draw.rect(icon, settings.COLOR_ICON_WALL, (0, 0, settings.ICON_SIZE, 4))
        self.pg.draw.rect(icon, settings.COLOR_ICON_WALL, (0, settings.ICON_SIZE - 4, settings.ICON_SIZE, 4))
        self.pg.draw.rect(icon, settings.COLOR_ICON_WALL, (0, 0, 4, settings.ICON_SIZE))
        self.pg.draw.rect(icon, settings.COLOR_ICON_WALL, (settings.ICON_SIZE - 4, 0, 4, settings.ICON_SIZE))

        self.pg.draw.rect(icon, settings.COLOR_ICON_WALL, (8, 8, 16, 4))
        self.pg.draw.rect(icon, settings.COLOR_ICON_WALL, (8, 20, 16, 4))
        self.pg.draw.rect(icon, settings.COLOR_ICON_PATH, (12, 12, 8, 8))
        self.pg.draw.circle(icon, settings.COLOR_ICON_PLAYER, (16, 16), 4)

        return icon

    @property
    def collected(self) -> int:
        return self.model.collected

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
                        self.ui_state = "playing"
                elif event.key == self.pg.K_r:
                    self.model.new_game(self.model.difficulty)
                elif self.model.status == "playing":
                    if event.key == self.pg.K_p:
                        self.ui_state = "paused"
                        self.menu_selected = 0
                    elif event.key == self.pg.K_SPACE:
                        self.model.use_escape_blink()
                    else:
                        self.start_held_movement(event.key)
                elif event.key in (self.pg.K_RETURN, self.pg.K_SPACE):
                    next_difficulty = self.model.next_difficulty() if self.model.status == "won" else self.model.difficulty
                    self.model.new_game(next_difficulty)
                    self.ui_state = "playing"

    def _perform_movement(self, direction: Cell) -> None:
        self.model.held_direction = direction
        self.model.try_move(direction)
        self.model.move_timer = settings.PLAYER_MOVE_DELAY

    def start_held_movement(self, key: int) -> None:
        direction = self.direction_for_key(key)
        if direction is None:
            return
        self._perform_movement(direction)

    def update_held_movement(self, dt: float) -> None:
        self.model.move_timer = max(0.0, self.model.move_timer - dt)
        direction = self.current_held_direction()

        if direction is None:
            self.model.held_direction = None
            return

        if self.model.move_timer <= 0:
            self._perform_movement(direction)

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
        if self.ui_state != "playing":
            return

        if self.model.status != "playing":
            return

        self.model.update(dt)
        self.update_held_movement(dt)

    def draw(self) -> None:
        self.screen.fill(settings.COLOR_BG)

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

        title = self.font.render("Maze Escape", True, settings.COLOR_TITLE_TEXT)
        self.screen.blit(title, (settings.TITLE_POS_X, settings.TITLE_POS_Y))

        self.draw_stat_card(
            settings.SCREEN_WIDTH - 322,
            settings.COLOR_STAT_CRYSTAL,
            f"{self.collected}/{self.model.crystal_count}",
            "crystal",
        )
        self.draw_stat_card(
            settings.SCREEN_WIDTH - 214,
            settings.COLOR_STAT_STEPS,
            str(self.model.steps),
            "steps",
        )
        self.draw_stat_card(
            settings.SCREEN_WIDTH - 106,
            settings.COLOR_STAT_BLINK,
            self.blink_label(),
            "blink",
        )
        difficulty = settings.DIFFICULTY_LABELS.get(self.model.difficulty, "Средне")
        diff_text = self.small_font.render(f"Сложность: {difficulty}", True, settings.COLOR_MUTED_TEXT)
        self.screen.blit(diff_text, (settings.DIFFICULTY_POS_X, settings.DIFFICULTY_POS_Y))

    def draw_hud_background(self) -> None:
        top = settings.COLOR_HUD_TOP
        bottom = settings.COLOR_HUD_BOTTOM
        for y in range(settings.HUD_HEIGHT):
            factor = y / max(1, settings.HUD_HEIGHT - 1)
            color = tuple(
                int(top[i] + (bottom[i] - top[i]) * factor)
                for i in range(3)
            )
            self.pg.draw.line(self.screen, color, (0, y), (settings.SCREEN_WIDTH, y))

        self.pg.draw.line(
            self.screen,
            settings.COLOR_HUD_LINE,
            (0, settings.HUD_HEIGHT - 1),
            (settings.SCREEN_WIDTH, settings.HUD_HEIGHT - 1),
            2,
        )

    def draw_stat_card(self, x: int, color: tuple[int, int, int], value: str, icon: str) -> None:
        rect = self.pg.Rect(x, settings.STAT_CARD_Y, settings.STAT_CARD_WIDTH, settings.STAT_CARD_HEIGHT)
        self.pg.draw.rect(self.screen, settings.COLOR_CARD_BG, rect, border_radius=7)
        self.pg.draw.rect(self.screen, settings.COLOR_CARD_BORDER, rect, 1, border_radius=7)

        icon_center = (x + settings.STAT_ICON_OFFSET_X, settings.STAT_ICON_CENTER_Y)
        if icon == "crystal":
            self.draw_crystal_icon(icon_center, color)
        elif icon == "steps":
            self.draw_steps_icon(icon_center, color)
        else:
            self.draw_blink_icon(icon_center, color)

        text = self.small_font.render(value, True, settings.COLOR_CARD_TEXT)
        text_rect = text.get_rect(midleft=(x + settings.STAT_TEXT_OFFSET_X, settings.STAT_ICON_CENTER_Y))
        self.screen.blit(text, text_rect)

    def blink_label(self) -> str:
        if self.model.escape_cooldown <= 0:
            return "OK"
        return f"{self.model.escape_cooldown:.1f}s"

    def draw_crystal_icon(self, center: Cell, color: tuple[int, int, int]) -> None:
        x, y = center
        points = [(x, y - 10), (x + 8, y), (x, y + 10), (x - 8, y)]
        self.pg.draw.polygon(self.screen, color, points)
        self.pg.draw.polygon(self.screen, settings.COLOR_CRYSTAL_HIGHLIGHT, [(x, y - 7), (x + 4, y), (x, y + 3)])

    def draw_steps_icon(self, center: Cell, color: tuple[int, int, int]) -> None:
        x, y = center
        self.pg.draw.circle(self.screen, color, (x - 4, y + 4), 5)
        self.pg.draw.circle(self.screen, color, (x + 5, y - 5), 5)
        self.pg.draw.circle(self.screen, settings.COLOR_STEPS_HIGHLIGHT, (x - 5, y + 2), 2)

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
                    color = settings.COLOR_MAZE_UNSEEN
                elif cell in self.model.maze.walls:
                    color = settings.COLOR_MAZE_WALL_VISIBLE if cell in self.model.visible else settings.COLOR_MAZE_WALL_HIDDEN
                else:
                    color = settings.COLOR_MAZE_FLOOR_VISIBLE if cell in self.model.visible else settings.COLOR_MAZE_FLOOR_HIDDEN

                self.pg.draw.rect(self.screen, color, rect)

        exit_color = settings.COLOR_EXIT_READY if not self.model.crystals else settings.COLOR_EXIT_LOCKED
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
                self.pg.draw.circle(self.screen, settings.COLOR_STAT_CRYSTAL, (cx, cy), settings.CRYSTAL_RADIUS)
                self.pg.draw.circle(self.screen, settings.COLOR_CRYSTAL_HIGHLIGHT, (cx - 2, cy - 2), settings.CRYSTAL_GLOW_RADIUS)

    def draw_path_hint(self) -> None:
        if self.model.status != "playing":
            return

        for cell in self.model.hunter_path[1:10]:
            if cell not in self.model.revealed or cell in self.model.maze.walls:
                continue
            cx, cy = self.cell_center(cell)
            self.pg.draw.circle(self.screen, settings.COLOR_PATH_HINT, (cx, cy), settings.PATH_HINT_RADIUS)

    def draw_entities(self) -> None:
        px, py = self.cell_center(self.model.player)
        self.pg.draw.circle(self.screen, settings.COLOR_PLAYER, (px, py), settings.ENTITY_RADIUS)
        self.pg.draw.circle(self.screen, settings.COLOR_PLAYER_LIGHT, (px - 3, py - 3), settings.ENTITY_GLOW_RADIUS)

        if self.model.hunter in self.model.visible:
            hx, hy = self.cell_center(self.model.hunter)
            self.pg.draw.circle(self.screen, settings.COLOR_HUNTER, (hx, hy), settings.ENTITY_RADIUS)
            self.pg.draw.circle(self.screen, settings.COLOR_HUNTER_LIGHT, (hx - 3, hy - 3), settings.ENTITY_GLOW_RADIUS)

    def draw_overlay(self) -> None:
        overlay = self.pg.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), self.pg.SRCALPHA)
        overlay.fill(settings.COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        text = self.font.render(self.model.message, True, settings.COLOR_OVERLAY_TEXT)
        rect = text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        self.pg.draw.rect(
            self.screen,
            settings.COLOR_OVERLAY_BOX,
            rect.inflate(44, 28),
            border_radius=8,
        )
        self.screen.blit(text, rect)

    def draw_menu(self) -> None:
        title = self.font.render("Maze Escape", True, settings.COLOR_TITLE_TEXT)
        title_rect = title.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3 - 40))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render("Выберите уровень сложности:", True, settings.COLOR_SUBTITLE_TEXT)
        subtitle_rect = subtitle.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3 + 20))
        self.screen.blit(subtitle, subtitle_rect)

        for i, option in enumerate(self.menu_options):
            is_selected = i == self.menu_selected
            color = settings.COLOR_STAT_CRYSTAL if is_selected else settings.COLOR_SUBTITLE_TEXT
            
            if is_selected:
                opt_text = self.small_font.render(f"  > {option} <  ", True, color)
            else:
                opt_text = self.small_font.render(f"    {option}    ", True, color)
            
            rect = opt_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + i * settings.MENU_SPACING_Y))
            
            if is_selected:
                box = self.pg.Rect(
                    rect.x - settings.MENU_BOX_PADDING,
                    rect.y - settings.MENU_BOX_PADDING,
                    rect.width + settings.MENU_BOX_PADDING * 2,
                    rect.height + settings.MENU_BOX_PADDING * 2,
                )
                self.pg.draw.rect(self.screen, settings.COLOR_STAT_CRYSTAL, box, settings.MENU_BOX_BORDER)
            
            self.screen.blit(opt_text, rect)

    def draw_pause(self) -> None:
        overlay = self.pg.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), self.pg.SRCALPHA)
        overlay.fill(settings.COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("Пауза", True, settings.COLOR_TITLE_TEXT)
        title_rect = title.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)

        for i, option in enumerate(self.pause_options):
            is_selected = i == self.menu_selected
            color = settings.COLOR_STAT_CRYSTAL if is_selected else settings.COLOR_SUBTITLE_TEXT
            
            if is_selected:
                opt_text = self.small_font.render(f"  > {option} <  ", True, color)
            else:
                opt_text = self.small_font.render(f"    {option}    ", True, color)
            
            rect = opt_text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + i * settings.MENU_SPACING_Y))
            
            if is_selected:
                box = self.pg.Rect(
                    rect.x - settings.MENU_BOX_PADDING,
                    rect.y - settings.MENU_BOX_PADDING,
                    rect.width + settings.MENU_BOX_PADDING * 2,
                    rect.height + settings.MENU_BOX_PADDING * 2,
                )
                self.pg.draw.rect(self.screen, settings.COLOR_STAT_CRYSTAL, box, settings.MENU_BOX_BORDER)
            
            self.screen.blit(opt_text, rect)

    def cell_rect(self, cell: Cell):
        x, y = cell
        return self.pg.Rect(x * settings.TILE, settings.HUD_HEIGHT + y * settings.TILE, settings.TILE, settings.TILE)

    def cell_center(self, cell: Cell) -> Cell:
        x, y = cell
        return x * settings.TILE + settings.TILE // 2, settings.HUD_HEIGHT + y * settings.TILE + settings.TILE // 2
