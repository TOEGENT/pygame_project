from typing import List

import pygame
import sys
import math
import random


pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()


ACCELERATION = 500
FRICTION = 0.5
FIXED_DT = 1/120
accumulator = 0
PIXELS_PER_METER = 10 


class State:
    COLLISION = "Collision"
    NO_COLLISION = "No Collision"



class Colors:
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)

class Ball:
    def __init__(self, color, pos, radius, mass):
        self.color = color
        self.pos = [p / PIXELS_PER_METER for p in pos]  # Перевод в метры
        self.radius = radius / PIXELS_PER_METER  # Радиус в метрах
        self.mass = mass  # Масса в килограммах
        self.velocity = [0, 0]  # Скорость в м/с




class GameState:
    def __init__(self,*entites: List[Ball]):

        self.entities = entites[0]
        
    

 

    def apply_forces(self, dt):
        for i in range(len(self.entities)):
            a = self.entities[i]

            for j in range(i+1, len(self.entities)):
                b = self.entities[j]
                dx = a.pos[0] - b.pos[0]
                dy = a.pos[1] - b.pos[1]
                distance = math.sqrt(dx**2 + dy**2)

                if distance == 0:
                    continue

                nx = dx / distance
                ny = dy / distance

                R = a.radius + b.radius
                overlap = R - distance
                if overlap > 0:
                    # Сила пропорциональна скорости объектов
                    relative_speed = math.sqrt((a.velocity[0] - b.velocity[0])**2 + (a.velocity[1] - b.velocity[1])**2)
                    force = overlap * relative_speed * (a.mass * b.mass) / (a.mass + b.mass)
                    fx = nx * force
                    fy = ny * force

                    a.velocity[0] += fx / a.mass * dt
                    a.velocity[1] += fy / a.mass * dt
                    b.velocity[0] -= fx / b.mass * dt
                    b.velocity[1] -= fy / b.mass * dt
    
    def apply_boundaries(self, dt):
        w, h = screen.get_size()
        w /= PIXELS_PER_METER  # Ширина в метрах
        h /= PIXELS_PER_METER  # Высота в метрах

        for entity in self.entities:
            if entity.pos[0] - entity.radius < 0:
                entity.pos[0] = entity.radius
                entity.velocity[0] *= -0.5
            elif entity.pos[0] + entity.radius > w:
                entity.pos[0] = w - entity.radius
                entity.velocity[0] *= -0.5

            if entity.pos[1] - entity.radius < 0:
                entity.pos[1] = entity.radius
                entity.velocity[1] *= -0.5
            elif entity.pos[1] + entity.radius > h:
                entity.pos[1] = h - entity.radius
                entity.velocity[1] *= -0.5

    def check_input(self, dt):
        keys = pygame.key.get_pressed()
        player = self.entities[0]
        print(player.velocity)

        # Управление красным шаром
        if keys[pygame.K_LEFT]:
            player.velocity[0] -= ACCELERATION *dt
        if keys[pygame.K_RIGHT]:
            player.velocity[0] += ACCELERATION *dt
        if keys[pygame.K_UP]:
            player.velocity[1] -= ACCELERATION *dt
        if keys[pygame.K_DOWN]:
            player.velocity[1] += ACCELERATION * dt




    def update(self, dt):
        self.check_input(dt)

        self.apply_forces(dt)

        for entity in self.entities:

            entity.velocity[0] *= (1 - FRICTION*dt)
            entity.velocity[1] *= (1 - FRICTION*dt)

            entity.pos[0] += entity.velocity[0] * dt
            entity.pos[1] += entity.velocity[1] * dt

        self.apply_boundaries(dt)
        


running=True


balls = [Ball(
    color = random.choice([Colors.RED, Colors.BLUE]),
    pos = [random.randint(50, 750), random.randint(50, 550)],\
    radius = random.randint(2, 40), 
    mass = random.randint(2, 50)) for _ in range(10)]
enitites=balls
game_state = GameState(enitites)


# Главный игровой цикл
while running:

    dt = clock.tick(60) / 1000.0
    accumulator += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    while accumulator >= FIXED_DT:
        game_state.update(FIXED_DT)
        accumulator -= FIXED_DT

    # Отрисовка
    screen.fill(Colors.WHITE)
    for ball in game_state.entities:
        pygame.draw.circle(screen, ball.color, 
                           (int(ball.pos[0] * PIXELS_PER_METER), int(ball.pos[1] * PIXELS_PER_METER)), 
                           int(ball.radius * PIXELS_PER_METER))

    # Обновление кадра
    pygame.display.flip() 



pygame.quit()
sys.exit()