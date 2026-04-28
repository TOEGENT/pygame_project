from typing import List

import pygame
import sys
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")

SPEED = 1

class State:
    COLLISION = "Collision"
    NO_COLLISION = "No Collision"



class Colors:
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)

class Ball:
    def __init__(self,color,pos,radius):
        self.color = color
        self.pos = pos
        self.radius = radius
        self.dx=0
        self.dy=0

red_ball = Ball(Colors.RED,[100,300],30)
blue_ball = Ball(Colors.BLUE,[700,300],30)





class GameState:
    def __init__(self,player: Ball,*entites: List[Ball]):
        self.state = State.NO_COLLISION
        self.entities = list(entites)
        self.player = player
    

    def check_collision(self):
        for i in range(len(self.entities)):
            for j in range(i+1,len(self.entities)):
                e1 = self.entities[i]
                e2 = self.entities[j]
                distance = math.sqrt((e1.pos[0]-e2.pos[0])**2 + (e1.pos[1]-e2.pos[1])**2)
                if distance < e1.radius + e2.radius:
                    return State.COLLISION
        return State.NO_COLLISION

    def check_input(self):
        keys = pygame.key.get_pressed()

        # Управление красным шаром
        if keys[pygame.K_LEFT]:
            self.player.dx -= SPEED
        if keys[pygame.K_RIGHT]:
            self.player.dx += SPEED
        if keys[pygame.K_UP]:
            self.player.dy -= SPEED
        if keys[pygame.K_DOWN]:
            self.player.dy += SPEED

        if self.player.dx!=0 or self.player.dy!=0:
            length = math.sqrt(self.player.dx**2 + self.player.dy**2)
            self.player.dx=(self.player.dx/length)*SPEED
            self.player.dy=(self.player.dy/length)*SPEED
        
        self.player.pos[0] += dx
        self.player.pos[1] += dy

    def will_collide(self):
        original_pos = self.

    def update(self):
        self.state = self.check_collision()
        if self.state != State.COLLISION:
            self.check_input()
        

running=True
game_state = GameState(red_ball,red_ball,blue_ball)
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    

    game_state.update()

    # Отрисовка
    screen.fill(Colors.WHITE)
    pygame.draw.circle(screen,red_ball.color,red_ball.pos,red_ball.radius)
    pygame.draw.circle(screen,blue_ball.color,blue_ball.pos,blue_ball.radius)

    # Обновление кадра
    pygame.display.flip() 



pygame.quit()
sys.exit()