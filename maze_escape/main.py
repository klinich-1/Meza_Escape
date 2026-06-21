from __future__ import annotations

def run_game() -> int:
    try:
        import pygame
    except ImportError:
        print("PyGame is not installed. Install it with: python -m pip install pygame")
        return 1

    from maze_escape.app import Game

    pygame.init()
    Game(pygame).run()
    return 0


def main() -> int:
    return run_game()
