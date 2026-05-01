from __future__ import annotations

import sys
from typing import Optional, Sequence

from maze_escape.self_test import run_self_test


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
    args = list(sys.argv[1:] if argv is None else argv)

    if "--self-test" in args:
        return run_self_test()

    return run_game()
# Main

# Точка входа программы

# Управление аргументами командной строки
