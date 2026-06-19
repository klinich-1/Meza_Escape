from __future__ import annotations

import sys
from typing import Optional, Sequence


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


def main(argv: Optional[Sequence[str]] = None) -> int:
    _ = list(sys.argv[1:] if argv is None else argv)

    return run_game()
