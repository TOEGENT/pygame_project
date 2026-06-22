import config
import pygame
from pygame.locals import *
import sys
from game import game
Game = game.Game

pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Agar.io")

clock = pygame.time.Clock()
blue_font = pygame.font.Font(None,size=30)
red_font = pygame.font.Font(None,size=30)

game = Game(10*1000)


"""ball1 = ball.Ball((0,0),config.COLOR_BLUE,100,config.TEAM_BLUE)
game._add_ball(ball1)
ball2 = ball.Ball((100,100),config.COLOR_RED,100,config.TEAM_RED)
game._add_ball(ball2)
ball3 = ball.Ball((200,200),config.COLOR_BLUE,100,config.TEAM_BLUE)
game._add_ball(ball3)"""



game.start()
#cool_ball = list(game.balls)[-1]
#cool_ball.color = config.COLOR_BLACK
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255,255,255))

    red_points_text = red_font.render(str(game.red_score),True,config.COLOR_RED)
    blue_points_text = blue_font.render(str(game.blue_score),True,config.COLOR_BLUE)

    overlay_blue = pygame.Surface((config.WINDOW_WIDTH//2,config.WINDOW_HEIGHT),pygame.SRCALPHA)
    overlay_blue.fill((0,0,255,32))
    overlay_red = pygame.Surface((config.WINDOW_WIDTH//2,config.WINDOW_HEIGHT),pygame.SRCALPHA)
    overlay_red.fill((255,0,0,32))

    screen.blit(overlay_red,(config.WINDOW_WIDTH//2,0))
    screen.blit(overlay_blue,(0,0))
    screen.blit(blue_points_text,(config.WINDOW_WIDTH//2-40,15))
    screen.blit(red_points_text,(config.WINDOW_WIDTH//2+7,15))

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
            intent_pos = ball.pos[0]+intent.pos[0]*ball.speed, ball.pos[1]+intent.pos[1]*ball.speed
            pygame.draw.line(screen,intent.color,ball.pos,intent_pos,1)

        if ball.smooth_total_intent.color:
            total_intent_pos = (ball.pos[0]+ball.smooth_total_intent.pos[0]*ball.speed,
                        ball.pos[1]+ball.smooth_total_intent.pos[1]*ball.speed)
            pygame.draw.line(screen,ball.smooth_total_intent.color,ball.pos,total_intent_pos,1)

        
    for food in game.foods:
        pygame.draw.circle(screen,food.color, food.pos,food.radius)

    pygame.display.flip()
