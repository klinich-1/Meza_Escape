from __future__ import annotations

from dataclasses import dataclass
from typing import Set, Tuple


Cell = Tuple[int, int]


@dataclass
class Maze:
    walls: Set[Cell]
    floors: Set[Cell]
    cols: int
    rows: int

    def in_bounds(self, cell: Cell) -> bool:
        x, y = cell
        return 0 <= x < self.cols and 0 <= y < self.rows

    def passable(self, cell: Cell) -> bool:
        return self.in_bounds(cell) and cell in self.floors
# Исправления

# Комментарий к структуре лабиринта

# Уточнение метода проверки границ
