COLS = 31
ROWS = 21
TILE = 28
HUD_HEIGHT = 74

SCREEN_WIDTH = COLS * TILE
SCREEN_HEIGHT = ROWS * TILE + HUD_HEIGHT

FOV_RADIUS = 9
FOV_RAYS = 240

PLAYER_MOVE_DELAY = 0.1
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

FONT_TITLE_SIZE = 48
FONT_MENU_SIZE = 36

ICON_SIZE = 32

COLOR_BG = (7, 10, 18)

COLOR_ICON_BG = (16, 23, 33, 255)
COLOR_ICON_WALL = (29, 42, 58)
COLOR_ICON_PATH = (84, 190, 112)
COLOR_ICON_PLAYER = (91, 176, 214)

COLOR_TITLE_TEXT = (239, 241, 225)
COLOR_SUBTITLE_TEXT = (200, 200, 200)
COLOR_MUTED_TEXT = (150, 150, 150)

COLOR_HUD_TOP = (9, 12, 22)
COLOR_HUD_BOTTOM = (19, 24, 37)
COLOR_HUD_LINE = (48, 66, 82)

COLOR_CARD_BG = (25, 31, 45)
COLOR_CARD_BORDER = (48, 60, 76)
COLOR_CARD_TEXT = (226, 234, 226)

COLOR_STAT_CRYSTAL = (246, 207, 94)
COLOR_STAT_STEPS = (98, 176, 214)
COLOR_STAT_BLINK = (102, 214, 147)

COLOR_CRYSTAL_HIGHLIGHT = (255, 246, 172)
COLOR_STEPS_HIGHLIGHT = (184, 225, 238)

COLOR_MAZE_UNSEEN = (5, 7, 12)
COLOR_MAZE_WALL_VISIBLE = (29, 42, 58)
COLOR_MAZE_WALL_HIDDEN = (16, 23, 33)
COLOR_MAZE_FLOOR_VISIBLE = (36, 45, 43)
COLOR_MAZE_FLOOR_HIDDEN = (20, 27, 28)

COLOR_EXIT_READY = (84, 190, 112)
COLOR_EXIT_LOCKED = (142, 77, 62)

COLOR_PATH_HINT = (122, 55, 64)

COLOR_PLAYER = (91, 176, 214)
COLOR_PLAYER_LIGHT = (202, 244, 255)
COLOR_HUNTER = (216, 72, 82)
COLOR_HUNTER_LIGHT = (255, 168, 142)

COLOR_OVERLAY = (3, 5, 9, 178)
COLOR_OVERLAY_BOX = (28, 34, 43)
COLOR_OVERLAY_TEXT = (245, 240, 220)

STAT_CARD_WIDTH = 90
STAT_CARD_HEIGHT = 40
STAT_CARD_Y = 17
STAT_ICON_OFFSET_X = 19
STAT_ICON_CENTER_Y = 37
STAT_TEXT_OFFSET_X = 38

TITLE_POS_X = 18
TITLE_POS_Y = 19
DIFFICULTY_POS_X = 18
DIFFICULTY_POS_Y = 50

MENU_SPACING_Y = 50
MENU_BOX_PADDING = 5
MENU_BOX_BORDER = 2

ENTITY_RADIUS = 10
ENTITY_GLOW_RADIUS = 4
CRYSTAL_RADIUS = 7
CRYSTAL_GLOW_RADIUS = 3
PATH_HINT_RADIUS = 3
