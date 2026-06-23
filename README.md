# Agar.io (Pygame)

2D-симуляция в духе Agar.io: команды синих и красных шаров, нейтральная еда, AI на слоях intent, spatial hash для соседей.

## Запуск

```bash
pip install pygame pytest
python main.py
```

Тесты:

```bash
pytest tests/
```

## Управление

- **Меню:** Play, число противников (1–8), количество еды, размер карты (400 / 500 / 700).
- **В игре:** мышь — движение синей команды; **Space** — split всех своих шаров к курсору.
- Матч длится **3 минуты**; победитель — команда с большей суммарной массой.

## Структура проекта

```
main.py          # меню, HUD, игровой цикл, отрисовка
view.py          # отрисовка team blobs (MVC: View)
config.py        # константы
game/game.py     # Game, физика, spatial hash, split, spawn
ai/ai.py         # многослойный AI (food, balls, wall, wander, command)
entities/        # Ball, Food, Intent
utils/           # calc_intent, геометрия, тактика команд
tests/           # unit-тесты utils
```

Подробнее: `architecture.md`

## Алгоритмы (для отчёта)

| Сложность | Алгоритмы |
|-----------|-----------|
| **Лёгкие** | `calc_normal`, `calc_importance_factor`, `calc_mass_center`, `smooth_add_pos`, `team_mass_ratio`, `team_tactic`, `orbit_target` |
| **Средние** | Spatial hash (`get_ball_cells`, `update_hash`, `get_neighbours`); бюджет intent (`_apply_intent_budget`); `calc_intent` с tanh; карта плотности еды; поедание в `update_interseptions` |
| **Сложные** | Pipeline AI: 5 слоёв intent → нормализация → сглаживание → view_point; тактики defense / neutral / attack по `mass_ratio`; split по тактике и карте еды |

## Зависимости

- Python 3.10+
- pygame
- pytest (только для тестов)
