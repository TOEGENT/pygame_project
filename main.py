from typing import List

import pygame
import sys
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")

SPEED = 0.001
FRICTION = 0.0005

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
        
    

    @staticmethod
    def resolve_collision(ball, other):
        # Вычисляем нормальный вектор

        normal = [other.pos[0] - ball.pos[0], other.pos[1] - ball   .pos[1]]
        distance = math.sqrt(normal[0]**2 + normal[1]**2)
        if distance == 0:
            return  # Избегаем деления на ноль
        normal[0] /= distance
        normal[1] /= distance

        # Вычисляем относительную скорость
        relative_velocity = [ball.velocity[0] - other.velocity[0],
                             ball.velocity[1] - other.velocity[1]]

        # Вычисляем скорость по нормали
        velocity_along_normal = relative_velocity[0] * normal[0] + relative_velocity[1] * normal[1]

        if velocity_along_normal > 0:
            return  # Шары уже разлетаются

        # Вычисляем коэффициент упругости (для идеального столкновения он равен 1)
        restitution = 1

        # Вычисляем импульс
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= (1 / ball.mass + 1 / other.mass)

        impulse = [impulse_scalar * normal[0], impulse_scalar * normal[1]]

        # Применяем импульс к шарам
        ball.velocity[0] += impulse[0] / ball.mass
        ball.velocity[1] += impulse[1] / ball.mass
        other.velocity[0] -= impulse[0] / other.mass
        other.velocity[1] -= impulse[1] / other.mass

    def check_collisions(self):


        for i in range(len(self.entities)):
            entity1 = self.entities[i]

            for j in range(i+1, len(self.entities)):
                entity2 = self.entities[j]
                dx = entity1.pos[0] - entity2.pos[0]
                dy = entity1.pos[1] - entity2.pos[1]
                distance = math.sqrt(dx**2 + dy**2)

                if distance < entity1.radius + entity2.radius:
                    self.resolve_collision(entity1, entity2)
            
            if entity1.pos[0] - entity1.radius < 0 or entity1.pos[0] + entity1.radius > 800:
                entity1.velocity[0] = -entity1.velocity[0]
                entity1.pos[0] = max(entity1.radius, min(screen.get_width() - entity1.radius, entity1.pos[0]))
            if entity1.pos[1] - entity1.radius < 0 or entity1.pos[1] + entity1.radius > 600:
                entity1.velocity[1] = -entity1.velocity[1]
                entity1.pos[1] = max(entity1.radius, min(screen.get_height() - entity1.radius, entity1.pos[1]))

    def check_input(self):
        keys = pygame.key.get_pressed()
        player = self.entities[0]
        print(player.velocity)

        # Управление красным шаром
        if keys[pygame.K_LEFT]:
            player.velocity[0] -= SPEED
        if keys[pygame.K_RIGHT]:
            player.velocity[0] += SPEED
        if keys[pygame.K_UP]:
            player.velocity[1] -= SPEED
        if keys[pygame.K_DOWN]:
            player.velocity[1] += SPEED


        
        player.velocity[0] *= (1 - FRICTION)
        player.velocity[1] *= (1 - FRICTION)
        
        player.pos[0] += player.velocity[0]
        player.pos[1] += player.velocity[1]


    def update(self):
        self.check_input()

        for entity in self.entities:

            entity.velocity[0] *= (1 - FRICTION)

            entity.pos[0] += entity.velocity[0]
            entity.pos[1] += entity.velocity[1]
        
        self.check_collisions()


running=True
enitites=[red_ball,blue_ball]
game_state = GameState(enitites)

# Главный игровой цикл
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