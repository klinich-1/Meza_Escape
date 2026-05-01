# Maze Escape

A small PyGame maze game.

## Run

```powershell
python -m maze_escape
```

Controls:

- Hold `WASD` or arrows: move.
- `Space`: blink to a safer nearby passage.
- `R`: restart.
- `Esc`: quit.

Run algorithm checks without opening the game window:

```powershell
python -m maze_escape --self-test
```

## Structure

```text
maze_escape/
  __main__.py
  algorithms.py
  app.py
  main.py
  maze.py
  self_test.py
  settings.py
```

## Разработка проекта

Проект развивается через последовательные улучшения логики игры, генерации лабиринта и проверки алгоритмов.

## Algorithms

- `generate_maze()` in `algorithms.py`: randomized DFS maze generation.
- `astar()` in `algorithms.py`: enemy pathfinding.
- `raycast_fov()` in `algorithms.py`: fog of war visibility.
# Обновление от 3 мая
