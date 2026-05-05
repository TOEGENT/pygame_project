from turtle import distance
from typing import List

import pygame
import sys
import math
import random


pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()


ACCELERATION = 500
FRICTION = 0.5
FIXED_DT = 1/120
accumulator = 0
PIXELS_PER_METER = 10 
HEIGHT = 2000
WIDTH = 2000

MAX_MASS = 50
MIN_ALPHA = 0
MAX_ALPHA = 255

def draw_grid(surface,camera_offset,screen_width,screen_height,cell_size,color):

    offset_x,offset_y = camera_offset[0]*PIXELS_PER_METER,camera_offset[1]*PIXELS_PER_METER

    cell_px = cell_size * PIXELS_PER_METER


    start_x = int(-offset_x % cell_px)
    start_y = int(-offset_y % cell_px)
    for x in range(start_x, screen_width, cell_px):
        pygame.draw.line(surface, color, (x, 10), (x, screen_height))
    for y in range(start_y, screen_height, cell_px):
        pygame.draw.line(surface, color, (10, y), (screen_width, y))


def draw_ball_with_alpha(surface,color,position,radius,alpha):
    temp_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    temp_color = (*color, int(alpha))
    pygame.draw.circle(temp_surface, temp_color, (radius, radius), radius)
    surface.blit(temp_surface, (position[0] - radius, position[1] - radius))



class Camera:
    def __init__(self,width,height):
        self.offset = [0,0]
        self.width = width
        self.height = height

    def update(self,target_pos):
        self.offset[0] = target_pos[0]-(self.width / (2*PIXELS_PER_METER))
        self.offset[1] = target_pos[1]-(self.height / (2*PIXELS_PER_METER))
    
    def apply(self,target_pos):
        return [(target_pos[0] - self.offset[0])*PIXELS_PER_METER,(target_pos[1]-self.offset[1])*PIXELS_PER_METER]


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
        self.pos = pos
        self.radius = radius  # Радиус в метрах
        self.mass = mass  # Масса в килограммах
        self.velocity = [0, 0]  # Скорость в м/с




class GameState:
    def __init__(self,*entites: List[Ball]):

        self.entities = entites[0]
        
    
    def apply_absorption(self, dt):
        k = 2

        for i in range(len(self.entities)):
            for j in range(i+1, len(self.entities)):
                a = self.entities[i]
                b = self.entities[j]
                dx = a.pos[0] - b.pos[0]
                dy = a.pos[1] - b.pos[1]
                distance = math.sqrt(dx**2 + dy**2)
                radius_sum = a.radius + b.radius
                if distance == 0:
                    continue
                
                overlap = radius_sum - distance
                if overlap <= 0:
                    continue

                if a.radius > b.radius:
                    big,small = a,b
                elif b.radius > a.radius:
                    big,small = b,a
                else:
                    continue
                
                mass_factor = abs((big.mass - small.mass))/max(big.mass, small.mass)
                radius_factor = small.radius / big.radius

                transfer_rate = k*overlap*mass_factor*radius_factor

                dm = transfer_rate * dt
                print(dm,overlap)
                dm = max(0, min(dm, small.mass))
                
                small.mass -= dm
                big.mass += dm
                small.radius -=dm
                big.radius +=dm
 

    def apply_forces(self, dt):
        k=2
        e = 0.5
        for i in range(len(self.entities)):

            
            a = self.entities[i]

            for j in range(i+1, len(self.entities)):
                b = self.entities[j]
                dx = a.pos[0] - b.pos[0]
                dy = a.pos[1] - b.pos[1]
                distance = math.sqrt(dx**2 + dy**2)
                radius_sum = a.radius + b.radius
                if distance == 0:
                    continue

                nx = dx / distance
                ny = dy / distance

                R = a.radius + b.radius
                overlap = R - distance
                if overlap > 0:
                    
                    rvx = a.velocity[0] - b.velocity[0]
                    rvy = a.velocity[1] - b.velocity[1]
                    vel_along_normal = rvx * nx + rvy * ny 

                    if vel_along_normal > 0:
                        continue
                    
                    vel_along_normal -= (abs(vel_along_normal) **k)
                    j_impulse = -(1 + e) * vel_along_normal
                    j_impulse /= (1 / a.mass + 1 / b.mass)

                    impulse_x = j_impulse * nx
                    impulse_y = j_impulse * ny


                    a.velocity[0] += impulse_x / a.mass * dt
                    a.velocity[1] += impulse_y / a.mass * dt
                    b.velocity[0] -= impulse_x / b.mass * dt
                    b.velocity[1] -= impulse_y / b.mass * dt

    def apply_boundaries(self, dt):
        w,h = WIDTH, HEIGHT

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
        player = self.entities[0]


        screen_center = [screen.get_width() / (2), screen.get_height() / (2)]
        
        mouse_x,mouse_y = pygame.mouse.get_pos()
        mouse_pos = [mouse_x,mouse_y]

        max_distance = math.sqrt((screen.get_width() / 2)**2 + (screen.get_height() / 2)**2)


        dx = mouse_pos[0] - screen_center[0]
        dy = mouse_pos[1] - screen_center[1]
        distance = math.sqrt(dx**2 + dy**2)

        acceleration_factor = distance / max_distance
        if distance > 0:
            nx = dx / distance
            ny = dy / distance

            player.velocity[0] += nx * ACCELERATION* acceleration_factor * dt / (player.mass*player.radius)
            player.velocity[1] += ny *ACCELERATION*acceleration_factor * dt / (player.mass*player.radius)
        # Управление красным шаром
        




    def update(self, dt):
        self.check_input(dt)
        self.apply_forces(dt)
        self.apply_absorption(dt)
        
        self.entities = [e for e in self.entities if e.mass > 0.05]

        for entity in self.entities:

            entity.velocity[0] *= (1 - FRICTION*dt)
            entity.velocity[1] *= (1 - FRICTION*dt)

            entity.pos[0] += entity.velocity[0] * dt
            entity.pos[1] += entity.velocity[1] * dt

        self.apply_boundaries(dt)
        


running=True

balls = [
    Ball(
    color = Colors.RED,
    pos = [400, 300],
    radius = 1,
    mass = 10),
]
balls+=[Ball(
    color = random.choice([Colors.RED, Colors.BLUE]),
    pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)],\
    radius = random.randint(1, 10), 
    mass = random.randint(2, 50)) for _ in range(100)]

entities=balls
game_state = GameState(entities)

camera = Camera(screen.get_width(),screen.get_height())


# Главный игровой цикл
while running:

    dt = clock.tick(60) / 1000.0
    accumulator += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    while accumulator >= FIXED_DT:
        game_state.update(FIXED_DT)
        camera.update(game_state.entities[0].pos)
        accumulator -= FIXED_DT

    # Отрисовка
    screen.fill(Colors.WHITE)
    draw_grid(screen,camera.offset,screen.get_width(),screen.get_height(),20,(200,200,200))
    for ball in game_state.entities:

        screen_pos = camera.apply(ball.pos)
        mass_norm = max(0, min(1, ball.mass / MAX_MASS))
        alpha = int(MIN_ALPHA + mass_norm * (MAX_ALPHA - MIN_ALPHA))
        draw_ball_with_alpha(screen, ball.color, screen_pos, int(ball.radius * PIXELS_PER_METER), alpha)

    # Обновление кадра
    pygame.display.flip() 



pygame.quit()
sys.exit()