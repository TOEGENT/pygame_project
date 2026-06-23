import config
import math
import pygame
from pygame.locals import *
import sys
from game import game
import view
Game = game.Game

INTENT_VIZ_BASE_LENGTH = 100
INTENT_VIZ_LOG_SCALE = 10

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

CONTROLS_HELP_LINES = (
    "Мышь — двигать шар",
    "ЛКМ — сильнее к курсору",
    "ПКМ — слабее / отступление",
    "СКМ — не реагировать на шары",
    "Пробел — разделить команду к курсору",
)


def make_font(size):
    for name in ("segoeui", "arial", "calibri", "tahoma"):
        path = pygame.font.match_font(name)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


class MenuSettings:
    def __init__(self):
        self.difficulty = config.DIFFICULTY_MEDIUM
        self.opponents = 2
        self.food = config.START_MASS
        self.map_size = config.DIFFICULTY_MAP_SIZE[config.DIFFICULTY_MEDIUM]
        self.player_mass = config.DIFFICULTY_PLAYER_MASS[config.DIFFICULTY_MEDIUM]

    def set_difficulty(self, mode):
        self.difficulty = mode
        if mode == config.DIFFICULTY_CUSTOM:
            return
        self.player_mass = config.DIFFICULTY_PLAYER_MASS[mode]
        self.map_size = config.DIFFICULTY_MAP_SIZE[mode]
        if mode == config.DIFFICULTY_EASY:
            self.opponents = 2
            self.food = 4000
        elif mode == config.DIFFICULTY_MEDIUM:
            self.opponents = 2
            self.food = config.START_MASS
        elif mode == config.DIFFICULTY_HARD:
            self.opponents = 4
            self.food = 6000

    def cycle_map_size(self, direction):
        self.difficulty = config.DIFFICULTY_CUSTOM
        options = list(config.MAP_SIZE_OPTIONS)
        try:
            idx = options.index(self.map_size)
        except ValueError:
            idx = 1
        idx = (idx + direction) % len(options)
        self.map_size = options[idx]


def intent_viz_tip(origin, vector, base_length=INTENT_VIZ_BASE_LENGTH, log_scale=INTENT_VIZ_LOG_SCALE):
    ox, oy = origin
    vx, vy = vector[0], vector[1]
    magnitude = math.hypot(vx, vy)
    if magnitude < 1e-9:
        return origin
    viz_length = min(base_length, log_scale * math.log1p(magnitude))
    return (ox + vx / magnitude * viz_length, oy + vy / magnitude * viz_length)


def draw_button(screen, rect, label, font, hover=False, active=False):
    if active:
        color = (180, 200, 255)
    elif hover:
        color = (220, 220, 230)
    else:
        color = (200, 200, 210)
    pygame.draw.rect(screen, color, rect, border_radius=6)
    border = (40, 80, 180) if active else (80, 80, 90)
    pygame.draw.rect(screen, border, rect, 2, border_radius=6)
    text = font.render(label, True, (30, 30, 40))
    screen.blit(text, text.get_rect(center=rect.center))


def format_time(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


def draw_centered_lines(screen, lines, font, y_start, line_height, color=(50, 50, 60)):
    for i, line in enumerate(lines):
        surf = font.render(line, True, color)
        screen.blit(surf, surf.get_rect(center=(config.MENU_WIDTH // 2, y_start + i * line_height)))


def draw_controls_help(screen, font, center_x, y_start, line_height=17, color=(90, 90, 100)):
    for i, line in enumerate(CONTROLS_HELP_LINES):
        surf = font.render(line, True, color)
        screen.blit(surf, surf.get_rect(center=(center_x, y_start + i * line_height)))


def run_menu(screen, settings, fonts):
    title_font, label_font, btn_font = fonts
    small_font = make_font(22)
    hint_font = make_font(19)
    play_rect = pygame.Rect(150, 565, 200, 50)

    diff_y = 130
    diff_btn_w = 115
    diff_gap = 8
    diff_start_x = (config.MENU_WIDTH - (4 * diff_btn_w + 3 * diff_gap)) // 2
    difficulty_buttons = [
        (config.DIFFICULTY_EASY, "Лёгкий"),
        (config.DIFFICULTY_MEDIUM, "Средний"),
        (config.DIFFICULTY_HARD, "Сложный"),
        (config.DIFFICULTY_CUSTOM, "Свой"),
    ]
    diff_rects = {}
    for i, (mode, label) in enumerate(difficulty_buttons):
        x = diff_start_x + i * (diff_btn_w + diff_gap)
        diff_rects[mode] = (pygame.Rect(x, diff_y, diff_btn_w, 36), label)

    row_y = [300, 355, 410, 465]
    custom_rows = [
        {
            "name": "Соперники",
            "y": row_y[0],
            "dec": pygame.Rect(50, row_y[0], 44, 36),
            "inc": pygame.Rect(406, row_y[0], 44, 36),
            "value": lambda: settings.opponents,
            "dec_fn": lambda: setattr(
                settings,
                "opponents",
                max(config.MENU_OPPONENTS_MIN, settings.opponents - 1),
            ),
            "inc_fn": lambda: setattr(
                settings,
                "opponents",
                min(config.MENU_OPPONENTS_MAX, settings.opponents + 1),
            ),
        },
        {
            "name": "Еда",
            "y": row_y[1],
            "dec": pygame.Rect(50, row_y[1], 44, 36),
            "inc": pygame.Rect(406, row_y[1], 44, 36),
            "value": lambda: settings.food,
            "dec_fn": lambda: setattr(
                settings,
                "food",
                max(config.MENU_FOOD_MIN, settings.food - config.MENU_FOOD_STEP),
            ),
            "inc_fn": lambda: setattr(
                settings,
                "food",
                min(config.MENU_FOOD_MAX, settings.food + config.MENU_FOOD_STEP),
            ),
        },
        {
            "name": "Карта",
            "y": row_y[2],
            "dec": pygame.Rect(50, row_y[2], 44, 36),
            "inc": pygame.Rect(406, row_y[2], 44, 36),
            "value": lambda: settings.map_size,
            "dec_fn": lambda: settings.cycle_map_size(-1),
            "inc_fn": lambda: settings.cycle_map_size(1),
        },
        {
            "name": "Ваша масса",
            "y": row_y[3],
            "dec": pygame.Rect(50, row_y[3], 44, 36),
            "inc": pygame.Rect(406, row_y[3], 44, 36),
            "value": lambda: int(settings.player_mass),
            "dec_fn": lambda: setattr(
                settings,
                "player_mass",
                max(config.MINIMUM_MASS * 2, settings.player_mass - 50),
            ),
            "inc_fn": lambda: setattr(
                settings,
                "player_mass",
                min(1500, settings.player_mass + 50),
            ),
        },
    ]

    def preset_summary_lines():
        return [
            f"Карта: {settings.map_size}",
            f"Ваша масса: {int(settings.player_mass)}",
            f"Соперники: {settings.opponents}",
            f"Еда: {settings.food}",
        ]

    while True:
        mouse_pos = pygame.mouse.get_pos()
        is_custom = settings.difficulty == config.DIFFICULTY_CUSTOM
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(mouse_pos):
                    return True
                for mode, (rect, _label) in diff_rects.items():
                    if rect.collidepoint(mouse_pos):
                        settings.set_difficulty(mode)
                if is_custom:
                    for row in custom_rows:
                        if row["dec"].collidepoint(mouse_pos):
                            settings.difficulty = config.DIFFICULTY_CUSTOM
                            row["dec_fn"]()
                        if row["inc"].collidepoint(mouse_pos):
                            settings.difficulty = config.DIFFICULTY_CUSTOM
                            row["inc_fn"]()

        screen.fill((245, 245, 250))
        title = title_font.render("Дуэлярио", True, config.COLOR_BLACK)
        screen.blit(title, title.get_rect(center=(config.MENU_WIDTH // 2, 70)))

        diff_lbl = label_font.render("Сложность", True, (50, 50, 60))
        screen.blit(diff_lbl, diff_lbl.get_rect(center=(config.MENU_WIDTH // 2, 110)))
        for mode, (rect, label) in diff_rects.items():
            draw_button(
                screen,
                rect,
                label,
                btn_font,
                rect.collidepoint(mouse_pos),
                active=settings.difficulty == mode,
            )

        help_lbl = label_font.render("Управление", True, (50, 50, 60))
        screen.blit(help_lbl, help_lbl.get_rect(center=(config.MENU_WIDTH // 2, 178)))
        draw_controls_help(screen, hint_font, config.MENU_WIDTH // 2, 200)

        if is_custom:
            for row in custom_rows:
                draw_button(screen, row["dec"], "-", btn_font, row["dec"].collidepoint(mouse_pos))
                draw_button(screen, row["inc"], "+", btn_font, row["inc"].collidepoint(mouse_pos))
                line = f"{row['name']}: {row['value']()}"
                line_surf = label_font.render(line, True, (30, 30, 40))
                screen.blit(line_surf, line_surf.get_rect(center=(config.MENU_WIDTH // 2, row["y"] + 18)))
        else:
            draw_centered_lines(
                screen,
                preset_summary_lines(),
                small_font,
                y_start=300,
                line_height=28,
            )

        draw_button(screen, play_rect, "Играть", btn_font, play_rect.collidepoint(mouse_pos))
        pygame.display.flip()
        pygame.time.Clock().tick(60)


def draw_hud(screen, game_obj, fonts):
    ui_font, timer_font, _ = fonts
    blue_mass = int(game_obj.team_mass(config.TEAM_BLUE))
    red_mass = int(game_obj.team_mass(config.TEAM_RED))
    screen.blit(ui_font.render(str(blue_mass), True, config.COLOR_BLUE), (10, 15))
    screen.blit(
        ui_font.render(str(red_mass), True, config.COLOR_RED),
        (config.WINDOW_WIDTH - 50, 15),
    )
    timer_text = timer_font.render(
        format_time(game_obj.match_time_remaining), True, config.COLOR_BLACK
    )
    screen.blit(timer_text, timer_text.get_rect(center=(config.WINDOW_WIDTH // 2, 22)))


def draw_game_over(screen, game_obj, fonts):
    title_font, _, btn_font = fonts
    overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 180))
    screen.blit(overlay, (0, 0))

    winner = game_obj.winner_team()
    if winner == config.TEAM_BLUE:
        msg = "Победа синих!"
        color = config.COLOR_BLUE
    elif winner == config.TEAM_RED:
        msg = "Победа красных!"
        color = config.COLOR_RED
    else:
        msg = "Ничья!"
        color = config.COLOR_BLACK

    if game_obj.match_time_remaining > 0:
        subtitle = "Команда уничтожена"
    else:
        subtitle = "Время вышло"
    time_surf = title_font.render(subtitle, True, config.COLOR_BLACK)
    screen.blit(
        time_surf,
        time_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 50)),
    )
    win_surf = title_font.render(msg, True, color)
    screen.blit(
        win_surf,
        win_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2)),
    )
    hint = btn_font.render("Click to menu", True, (60, 60, 70))
    screen.blit(
        hint,
        hint.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 60)),
    )


def run_match(settings):
    config.WINDOW_WIDTH = settings.map_size
    config.WINDOW_HEIGHT = settings.map_size
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Agar.io")

    clock = pygame.time.Clock()
    fonts = (
        pygame.font.Font(None, 36),
        pygame.font.Font(None, 32),
        pygame.font.Font(None, 28),
    )
    hint_font = pygame.font.Font(None, 22)
    game_obj = Game(0, control_mode=config.CONTROL_MODE_PLAYER)
    game_obj.reset_for_match(
        settings.opponents,
        settings.food,
        settings.map_size,
        settings.player_mass,
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not game_obj.is_over:
                    game_obj.split_player_team(pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONDOWN and game_obj.is_over:
                return

        screen.fill((255, 255, 255))
        if not game_obj.is_over:
            dt = clock.tick(60) / 1000
            game_obj.update(dt)
        else:
            clock.tick(60)

        draw_hud(screen, game_obj, fonts)

        view.draw_team_blobs(screen, game_obj.blue_blob, game_obj.red_blob)

        balls = sorted(game_obj.balls, key=lambda b: b.radius, reverse=True)
        for b in balls:
            pygame.draw.circle(screen, b.color, b.pos, b.radius)
            pygame.draw.circle(screen, config.COLOR_WHITE, b.pos, b.radius + 1, 1)
            #pygame.draw.circle(
            #    screen, b.color, b.pos, b.radius * config.BALL_VIEW_FACTOR, 2
            #)
            for intent in b.smooth_intents:
                intent_pos = intent_viz_tip(b.pos, intent.pos)
                if intent_pos != b.pos:
                    pygame.draw.line(screen, intent.color, b.pos, intent_pos, 1)
            if b.smooth_total_intent.color:
                total_intent_pos = intent_viz_tip(
                    b.pos,
                    b.smooth_total_intent.pos,
                    base_length=INTENT_VIZ_BASE_LENGTH + 8,
                )
                if total_intent_pos != b.pos:
                    pygame.draw.line(
                        screen,
                        b.smooth_total_intent.color,
                        b.pos,
                        total_intent_pos,
                        1,
                    )

        for food_item in game_obj.foods:
            pygame.draw.circle(screen, food_item.color, food_item.pos, food_item.radius)

        if game_obj.is_over:
            draw_game_over(screen, game_obj, fonts)

        pygame.display.flip()


def main():
    pygame.init()
    settings = MenuSettings()
    menu_fonts = (
        pygame.font.Font(None, 64),
        pygame.font.Font(None, 32),
        pygame.font.Font(None, 28),
    )
    screen = pygame.display.set_mode((config.MENU_WIDTH, config.MENU_HEIGHT))
    pygame.display.set_caption("Дуэлярио")

    while True:
        if not run_menu(screen, settings, menu_fonts):
            break
        run_match(settings)
        screen = pygame.display.set_mode((config.MENU_WIDTH, config.MENU_HEIGHT))

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
