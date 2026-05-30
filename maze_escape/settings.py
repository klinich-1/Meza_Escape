COLS = 31
ROWS = 21
TILE = 28
HUD_HEIGHT = 74

SCREEN_WIDTH = COLS * TILE
SCREEN_HEIGHT = ROWS * TILE + HUD_HEIGHT

CRYSTAL_COUNT = 6
FOV_RADIUS = 9
FOV_RAYS = 240

PLAYER_MOVE_DELAY = 0.1
ESCAPE_BLINK_RANGE = 6
ESCAPE_COOLDOWN = 5.0
HUNTER_STUN_AFTER_BLINK = 1.1

DIFFICULTY_LEVELS = ("easy", "medium", "hard")
DIFFICULTY_LABELS = {
    "easy": "Легко",
    "medium": "Средне",
    "hard": "Сложно",
}
DIFFICULTY_CONFIGS = {
    "easy": {
        "extra_passages_factor": 0.18,
        "fov_radius": 11,
        "escape_blink_range": 8,
        "escape_cooldown": 4.0,
        "hunter_speed_factor": 0.8,
        "crystal_count": 5,
    },
    "medium": {
        "extra_passages_factor": 0.12,
        "fov_radius": 9,
        "escape_blink_range": 6,
        "escape_cooldown": 5.0,
        "hunter_speed_factor": 1.6,
        "crystal_count": 6,
    },
    "hard": {
        "extra_passages_factor": 0.08,
        "fov_radius": 7,
        "escape_blink_range": 5,
        "escape_cooldown": 6.5,
        "hunter_speed_factor": 2.0,
        "crystal_count": 7,
    },
}

# UI: Fonts
FONT_TITLE_SIZE = 48
FONT_MENU_SIZE = 36
FONT_HUD_SIZE = 36

# UI: FPS and timing
FPS = 60

# UI: Colors (RGB tuples)
COLOR_BACKGROUND = (7, 10, 18)
COLOR_TEXT_LIGHT = (239, 241, 225)
COLOR_TEXT_NEUTRAL = (200, 200, 200)
COLOR_TEXT_MUTED = (150, 150, 150)
COLOR_TEXT_SCREEN = (245, 240, 220)
COLOR_ACCENT_YELLOW = (246, 207, 94)
COLOR_ACCENT_BLUE = (98, 176, 214)
COLOR_ACCENT_GREEN = (102, 214, 147)

COLOR_HUD_TOP = (9, 12, 22)
COLOR_HUD_BOTTOM = (19, 24, 37)
COLOR_HUD_BORDER = (48, 66, 82)
COLOR_OVERLAY_BG = (3, 5, 9, 178)
COLOR_OVERLAY_BOX = (28, 34, 43)

COLOR_CARD_BG = (25, 31, 45)
COLOR_CARD_BORDER = (48, 60, 76)

COLOR_STAT_CRYSTAL = (246, 207, 94)
COLOR_STAT_STEPS = (98, 176, 214)
COLOR_STAT_BLINK = (102, 214, 147)
COLOR_STAT_LIGHT = (226, 234, 226)
COLOR_STAT_ACCENT = (255, 246, 172)

COLOR_PLAYER = (91, 176, 214)
COLOR_PLAYER_LIGHT = (202, 244, 255)
COLOR_HUNTER = (216, 72, 82)
COLOR_HUNTER_LIGHT = (255, 168, 142)
COLOR_CRYSTAL = (246, 207, 94)
COLOR_CRYSTAL_LIGHT = (255, 246, 172)
COLOR_EXIT_READY = (84, 190, 112)
COLOR_EXIT_BLOCKED = (142, 77, 62)
COLOR_PATH_HINT = (122, 55, 64)

COLOR_MAZE_DARK = (5, 7, 12)
COLOR_MAZE_WALL_VISIBLE = (29, 42, 58)
COLOR_MAZE_WALL_HIDDEN = (16, 23, 33)
COLOR_MAZE_FLOOR_VISIBLE = (36, 45, 43)
COLOR_MAZE_FLOOR_HIDDEN = (20, 27, 28)

# UI: Positions and sizes
TITLE_POS = (18, 19)
DIFFICULTY_TEXT_POS = (18, 50)
STAT_CRYSTAL_X = SCREEN_WIDTH - 322
STAT_STEPS_X = SCREEN_WIDTH - 214
STAT_BLINK_X = SCREEN_WIDTH - 106
STAT_CARD_Y = 17
STAT_CARD_WIDTH = 90
STAT_CARD_HEIGHT = 40
STAT_ICON_X = 19
STAT_ICON_Y = 37

# UI: Icon sizes
ICON_CRYSTAL_SIZE = 8
ICON_STEPS_RADIUS = 5
ICON_BLINK_POINT = 8

# UI: Player and entities  
PLAYER_RADIUS = 10
PLAYER_GLOW_RADIUS = 4
HUNTER_RADIUS = 10
HUNTER_GLOW_RADIUS = 4
CRYSTAL_RADIUS = 7
CRYSTAL_GLOW_RADIUS = 3
PATH_HINT_RADIUS = 3

# UI: Card dimensions
OVERLAY_OPACITY = 178
OVERLAY_BOX_PADDING = 22
OVERLAY_BOX_RADIUS = 8
STAT_CARD_RADIUS = 7
STAT_CARD_BORDER = 1

# UI: Menu
MENU_SPACING = 50
MENU_ARROW = "  > {0} <  "
MENU_PLAIN = "    {0}    "
MENU_BOX_PADDING = 5
MENU_BOX_BORDER = 2

# Raycast FOV
RAYCAST_STEP_SIZE = 0.08
