import config
import pygame
from pygame.locals import *
import sys
import math
import random
from collections import defaultdict

from game import game
Game = game.Game

pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Agar.io")

clock = pygame.time.Clock()
blue_font = pygame.font.Font(None,size=30)
red_font = pygame.font.Font(None,size=30)

game = Game(10*1000,start_mass=5000)
game.start()
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
    for ball in game.balls:
        pygame.draw.circle(screen,ball.color, ball.pos,ball.radius)

    for food in game.foods:
        pygame.draw.circle(screen,food.color, food.pos,food.radius)


    pygame.display.flip()