agario/
│
├── main.py                # точка входа
├── config.py              # константы (без magic numbers)
│
├── core/                  # базовые абстракции
│   ├── vector.py          # математика (Vector2)
│   └── spatial_hash.py    # ускорение поиска соседей
│
├── models/                # модель
│   ├── entity.py          # базовая сущность
│   ├── player.py          # игрок
│   ├── bot.py             # AI-бот
│   └── food.py            # еда
│
├── systems/               # бизнес-логика
│   ├── movement_system.py
│   ├── collision_system.py
│   └── ai_system.py
│
├── game/                  # оркестрация
│   ├── game_state.py      # состояние игры
│   └── game.py            # главный игровой цикл
│
├── view/                  # представление (View)
│   └── renderer.py
│
├── input/                 # ввод (Controller часть)
│   └── input_handler.py
│
├── ui/                    # UX слой
│   └── menu.py
│
├── utils/
│   └── save_load.py
│
tests/
