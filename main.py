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


class MenuSettings:
    def __init__(self):
        self.opponents = 2
        self.food = config.START_MASS
        self.map_size = config.WINDOW_WIDTH

    def cycle_map_size(self, direction):
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


def draw_button(screen, rect, label, font, hover=False):
    color = (220, 220, 230) if hover else (200, 200, 210)
    pygame.draw.rect(screen, color, rect, border_radius=6)
    pygame.draw.rect(screen, (80, 80, 90), rect, 2, border_radius=6)
    text = font.render(label, True, (30, 30, 40))
    screen.blit(text, text.get_rect(center=rect.center))


def format_time(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


def run_menu(screen, settings, fonts):
    title_font, label_font, btn_font = fonts
    play_rect = pygame.Rect(150, 430, 200, 50)
    rows = []

    def add_row(y, label, dec_rect, val_text, inc_rect):
        rows.append((label, dec_rect, val_text, inc_rect, y))

    opp_y = 180
    food_y = 250
    map_y = 320
    add_row(
        opp_y,
        "Opponents",
        pygame.Rect(80, opp_y, 40, 36),
        lambda: str(settings.opponents),
        pygame.Rect(380, opp_y, 40, 36),
    )
    add_row(
        food_y,
        "Food",
        pygame.Rect(80, food_y, 40, 36),
        lambda: str(settings.food),
        pygame.Rect(380, food_y, 40, 36),
    )
    add_row(
        map_y,
        "Map size",
        pygame.Rect(80, map_y, 40, 36),
        lambda: str(settings.map_size),
        pygame.Rect(380, map_y, 40, 36),
    )

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(mouse_pos):
                    return True
                if pygame.Rect(80, opp_y, 40, 36).collidepoint(mouse_pos):
                    settings.opponents = max(
                        config.MENU_OPPONENTS_MIN,
                        settings.opponents - 1,
                    )
                if pygame.Rect(380, opp_y, 40, 36).collidepoint(mouse_pos):
                    settings.opponents = min(
                        config.MENU_OPPONENTS_MAX,
                        settings.opponents + 1,
                    )
                if pygame.Rect(80, food_y, 40, 36).collidepoint(mouse_pos):
                    settings.food = max(
                        config.MENU_FOOD_MIN,
                        settings.food - config.MENU_FOOD_STEP,
                    )
                if pygame.Rect(380, food_y, 40, 36).collidepoint(mouse_pos):
                    settings.food = min(
                        config.MENU_FOOD_MAX,
                        settings.food + config.MENU_FOOD_STEP,
                    )
                if pygame.Rect(80, map_y, 40, 36).collidepoint(mouse_pos):
                    settings.cycle_map_size(-1)
                if pygame.Rect(380, map_y, 40, 36).collidepoint(mouse_pos):
                    settings.cycle_map_size(1)

        screen.fill((245, 245, 250))
        title = title_font.render("Agar.io", True, config.COLOR_BLACK)
        screen.blit(title, title.get_rect(center=(config.MENU_WIDTH // 2, 80)))

        for label, dec_rect, val_fn, inc_rect, y in rows:
            lbl = label_font.render(label, True, (50, 50, 60))
            screen.blit(lbl, (140, y + 6))
            draw_button(screen, dec_rect, "-", btn_font, dec_rect.collidepoint(mouse_pos))
            val = btn_font.render(val_fn(), True, (30, 30, 40))
            screen.blit(val, val.get_rect(center=(config.MENU_WIDTH // 2, y + 18)))
            draw_button(screen, inc_rect, "+", btn_font, inc_rect.collidepoint(mouse_pos))

        draw_button(screen, play_rect, "Play", btn_font, play_rect.collidepoint(mouse_pos))
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
        msg = "Blue wins!"
        color = config.COLOR_BLUE
    elif winner == config.TEAM_RED:
        msg = "Red wins!"
        color = config.COLOR_RED
    else:
        msg = "Draw!"
        color = config.COLOR_BLACK

    time_surf = title_font.render("Time's up", True, config.COLOR_BLACK)
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
    game_obj = Game(0, control_mode=config.CONTROL_MODE_PLAYER)
    game_obj.reset_for_match(settings.opponents, settings.food, settings.map_size)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not game_obj.is_over:
                    game_obj.split_player_team(pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONDOWN and game_obj.is_over:
                return screen

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
    pygame.display.set_caption("Agar.io")

    while True:
        if not run_menu(screen, settings, menu_fonts):
            break
        screen = run_match(settings)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
