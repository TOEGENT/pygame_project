import config
import math
import pygame
from pygame.locals import *
import sys
from game import game
from entities import ball
Game = game.Game

INTENT_VIZ_BASE_LENGTH = 100
INTENT_VIZ_LOG_SCALE = 10


def intent_viz_tip(origin, vector, base_length=INTENT_VIZ_BASE_LENGTH, log_scale=INTENT_VIZ_LOG_SCALE):
    ox, oy = origin
    vx, vy = vector[0], vector[1]
    magnitude = math.hypot(vx, vy)
    if magnitude < 1e-9:
        return origin
    viz_length = min(base_length, log_scale * math.log1p(magnitude))
    return (ox + vx / magnitude * viz_length, oy + vy / magnitude * viz_length)

pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
caption = "Agar.io — AI vs AI" if config.CONTROL_MODE == config.CONTROL_MODE_AI_VS_AI else "Agar.io"
pygame.display.set_caption(caption)

clock = pygame.time.Clock()
blue_font = pygame.font.Font(None, size=30)
red_font = pygame.font.Font(None, size=30)

game = Game(10*1000)


ball1 = ball.Ball((0,0),config.COLOR_BLUE,100,config.TEAM_BLUE)
game._add_ball(ball1)
ball2 = ball.Ball((100,100),config.COLOR_RED,100,config.TEAM_RED)
game._add_ball(ball2)



game.start()
#cool_ball = list(game.balls)[-1]
#cool_ball.color = config.COLOR_BLACK
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if game.player_ball:
                game.split_ball(game.player_ball)

    screen.fill((255,255,255))

    blue_mass = int(game.team_mass(config.TEAM_BLUE))
    red_mass = int(game.team_mass(config.TEAM_RED))
    blue_points_text = blue_font.render(str(blue_mass), True, config.COLOR_BLUE)
    red_points_text = red_font.render(str(red_mass), True, config.COLOR_RED)
    screen.blit(blue_points_text, (10, 15))
    screen.blit(red_points_text, (config.WINDOW_WIDTH - 50, 15))

    dt = clock.tick(60)/1000

    game.update(dt)
    game.draw_team_blobs(screen)

    balls = list(game.balls)
    balls.sort(key=lambda b: b.radius,reverse=True)
    for ball in balls:

        pygame.draw.circle(screen,ball.color, ball.pos,ball.radius)
        pygame.draw.circle(screen,config.COLOR_WHITE, ball.pos,ball.radius+1,1)

        pygame.draw.circle(screen,ball.color, ball.pos,ball.radius*config.BALL_VIEW_FACTOR,2)
        for intent in ball.smooth_intents:
            intent_pos = intent_viz_tip(ball.pos, intent.pos)
            if intent_pos != ball.pos:
                pygame.draw.line(screen, intent.color, ball.pos, intent_pos, 1)

        if ball.smooth_total_intent.color:
            total_intent_pos = intent_viz_tip(
                ball.pos,
                ball.smooth_total_intent.pos,
                base_length=INTENT_VIZ_BASE_LENGTH + 8,
            )
            if total_intent_pos != ball.pos:
                pygame.draw.line(screen, ball.smooth_total_intent.color, ball.pos, total_intent_pos, 1)

        
    for food in game.foods:
        pygame.draw.circle(screen,food.color, food.pos,food.radius)

    pygame.display.flip()
