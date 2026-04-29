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
    def __init__(self,color,pos,radius,mass):
        self.color = color
        self.pos = pos
        self.radius = radius
        self.mass = mass
        self.velocity = [0,0]

red_ball = Ball(Colors.RED,[100,300],30,1)
blue_ball = Ball(Colors.BLUE,[700,300],30,1)




class GameState:
    def __init__(self,*entites: List[Ball]):

        self.entities = entites[0]
        
    


    def resolve_collision(self,other):
        # Вычисляем нормальный вектор
        normal = [other.pos[0] - self.player.pos[0], other.pos[1] - self.player.pos[1]]
        distance = math.sqrt(normal[0]**2 + normal[1]**2)
        if distance == 0:
            return  # Избегаем деления на ноль
        normal[0] /= distance
        normal[1] /= distance

        # Вычисляем относительную скорость
        relative_velocity = [self.player.velocity[0] - other.velocity[0],
                             self.player.velocity[1] - other.velocity[1]]

        # Вычисляем скорость по нормали
        velocity_along_normal = relative_velocity[0] * normal[0] + relative_velocity[1] * normal[1]

        if velocity_along_normal > 0:
            return  # Шары уже разлетаются

        # Вычисляем коэффициент упругости (для идеального столкновения он равен 1)
        restitution = 1

        # Вычисляем импульс
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= (1 / self.player.mass + 1 / other.mass)

        impulse = [impulse_scalar * normal[0], impulse_scalar * normal[1]]

        # Применяем импульс к шарам
        self.player.velocity[0] += impulse[0] / self.player.mass
        self.player.velocity[1] += impulse[1] / self.player.mass
        other.velocity[0] -= impulse[0] / other.mass
        other.velocity[1] -= impulse[1] / other.mass

    def check_collision(self,other):
        dx = self.player.pos[0] - other.pos[0]
        dy = self.player.pos[1] - other.pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.player.radius + other.radius:
            self.resolve_collision(other)


    def check_input(self):
        keys = pygame.key.get_pressed()
        player = self.entities[0]
        # Управление красным шаром
        if keys[pygame.K_LEFT]:
            self.player.velocity[0] -= SPEED
        if keys[pygame.K_RIGHT]:
            self.player.velocity[0] += SPEED
        if keys[pygame.K_UP]:
            self.player.velocity[1] -= SPEED
        if keys[pygame.K_DOWN]:
            self.player.velocity[1] += SPEED

        if self.player.velocity[0]!=0 or self.player.velocity[1]!=0:
            length = math.sqrt(self.player.velocity[0]**2 + self.player.velocity[1]**2)
            self.player.velocity[0]=(self.player.velocity[0]/length)*SPEED
            self.player.velocity[1]=(self.player.velocity[1]/length)*SPEED
        
        self.player.pos[0] += self.player.velocity[0]
        self.player.pos[1] += self.player.velocity[1]


    def update(self,entities):
        for entity in entities:
            entity.pos[0] += entity.velocity[0]
            entity.pos[1] += entity.velocity[1]

running=True
enitites=[red_ball,blue_ball]
game_state = GameState(enitites)
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    for entity in game_state.entities:
        entity.update()
    
    for i in range(len(game_state.entities)):
        for j in range(i+1,len(game_state.entities)):
            game_state.check_collision(game_state.entities[i],game_state.entities[j])
    
   

    # Отрисовка
    screen.fill(Colors.WHITE)
    pygame.draw.circle(screen,red_ball.color,red_ball.pos,red_ball.radius)
    pygame.draw.circle(screen,blue_ball.color,blue_ball.pos,blue_ball.radius)

    # Обновление кадра
    pygame.display.flip() 



pygame.quit()
sys.exit()