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


ACCELERATION = 200
FRICTION = 0.5
FIXED_DT = 1/30
accumulator = 0
PIXELS_PER_METER = 10 
HEIGHT = 2000
WIDTH = 2000

MAX_MASS = 500
MIN_ALPHA = 10
MAX_ALPHA = 255
MAX_RADIUS = 500



def edge_damping(x,p=2.0):
    core = 4.0 *x * (1.0-x)
    return max(0.0,core)**p

def sigmoid01(x, k=10, x0=0.5):
    return 1 / (1 + math.exp(-k * (x - x0)))

def draw_grid(surface,camera,screen_width,screen_height,cell_size,color):

    offset_x,offset_y = camera.offset[0]*PIXELS_PER_METER*camera.zoom,camera.offset[1]*PIXELS_PER_METER*camera.zoom

    cell_px = cell_size * PIXELS_PER_METER*camera.zoom


    start_x = int(-offset_x % cell_px)
    start_y = int(-offset_y % cell_px)
    x = start_x
    while x < screen_width:
        pygame.draw.line(surface, color, (x, 0), (x, screen_height))
        x += cell_px
    y = start_y
    while y < screen_height:
        pygame.draw.line(surface, color, (0, y), (screen_width, y))
        y += cell_px



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
        self.zoom = 1.0

    def update(self,target_pos,target_radius):
        alpha = 0.5
        target_zoom = 2.0/(max(target_radius,1)**alpha)
        self.zoom += (target_zoom - self.zoom) * 0.2

        target_offset_x = target_pos[0] - (self.width / (2*PIXELS_PER_METER*self.zoom))
        target_offset_y = target_pos[1] - (self.height / (2*PIXELS_PER_METER*self.zoom))


        self.offset[0] += (target_offset_x-self.offset[0]) *0.4
        self.offset[1] += (target_offset_y - self.offset[1])*0.4

    def apply(self,target_pos):
        return [(target_pos[0] - self.offset[0])*PIXELS_PER_METER*self.zoom,
                (target_pos[1]-self.offset[1])*PIXELS_PER_METER*self.zoom]


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
                if distance == 0:
                    continue
                
                
                if a.radius > b.radius:
                    big,small = a,b
                elif b.radius > a.radius:
                    big,small = b,a
                else:
                    continue

                if distance+small.radius > big.radius:
                    continue

                
                mass_factor = abs((big.mass - small.mass))/max(big.mass, small.mass)
                radius_factor = small.radius / big.radius
                overlap = big.radius - distance

                transfer_rate = k*overlap*mass_factor*radius_factor

                dm = transfer_rate * dt
                dm = max(0, min(dm, small.mass))
                
                small.mass -= dm
                big.mass += dm
                small.radius -=dm
                big.radius +=dm
 

    def apply_forces(self, dt):
        k=1.5
        for i in range(len(self.entities)):

            
            a = self.entities[i]

            for j in range(i+1, len(self.entities)):

                b = self.entities[j]

                m_a_norm = max(0.0, min(1.0, a.mass / MAX_MASS))
                r_a_norm = max(0.0, min(1.0, a.radius / MAX_RADIUS))
                m_b_norm = max(0.0, min(1.0, b.mass / MAX_MASS))
                r_b_norm = max(0.0, min(1.0, b.radius / MAX_RADIUS))
                m_avg_norm = (m_a_norm + m_b_norm) / 2.0
                r_avg_norm = (r_a_norm + r_b_norm) / 2.0

                size_bias = r_avg_norm
                density_bias = m_avg_norm / max(r_avg_norm, 0.1)
                bounce_score = 0.75 * size_bias + 0.25 * density_bias
                e = 0.02 + 0.18 * (1.0 - sigmoid01(bounce_score, k=8, x0=0.35))

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
                    
                    rvx = a.velocity[0] - b.velocity[0]
                    rvy = a.velocity[1] - b.velocity[1]
                    vel_along_normal = rvx * nx + rvy * ny 
        

                    if vel_along_normal > 0:
                        continue
                    
                    j_impulse = -(1 + e) * vel_along_normal
                    j_impulse /= (1 / a.mass + 1 / b.mass)

                    impulse_x = j_impulse * nx
                    impulse_y = j_impulse * ny


                    a.velocity[0] += impulse_x / a.mass 
                    a.velocity[1] += impulse_y / a.mass 
                    b.velocity[0] -= impulse_x / b.mass 
                    b.velocity[1] -= impulse_y / b.mass 

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

            m = max(0.0, min(1.0, player.mass / MAX_MASS))
            r = max(0.0, min(1.0, player.radius / MAX_RADIUS))
            mass_factor = 1-edge_damping(m, 2.5)
            radius_factor = 1.0 - edge_damping(r, 2.5)


            speed_factor = mass_factor*radius_factor


            player.velocity[0] += nx * ACCELERATION * acceleration_factor * dt * speed_factor
            player.velocity[1] += ny * ACCELERATION * acceleration_factor * dt * speed_factor
        # Управление красным шаром



    def update_ai(self, dt):

        for i in range(0,len(self.entities)):
            if self.entities[i] == self.entities[0]:
                continue

            total_force_x=0
            total_force_y=0  
            a = self.entities[i]
            
            for j in range(0, len(self.entities)):
                b = self.entities[j]

                dx = a.pos[0] - b.pos[0]
                dy = a.pos[1] - b.pos[1]
                distance = max(0.1, math.sqrt(dx**2 + dy**2))
                if distance > a.radius*10 + b.radius :
                    drift_strength =1
                    t = pygame.time.get_ticks() / 1000.0
                    total_force_x += random.uniform(-1, 1)*drift_strength
                    total_force_y += random.uniform(-1, 1)*drift_strength
                    continue
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     

                nx = dx / distance
                ny = dy / distance
                radius_delta = abs(a.radius - b.radius) / max(MAX_RADIUS, 1)
                radius_factor = 1.0 - sigmoid01(radius_delta, 10, 0.25)
                distance_factor = 1.0 - sigmoid01(distance / 200.0, 12, 0.5)
                

                if a.radius > b.radius:

                    total_force_x -= radius_factor*distance_factor*b.mass * nx
                    total_force_y -= radius_factor*distance_factor*b.mass * ny
                else:
                    total_force_x += radius_factor*distance_factor*a.mass * nx
                    total_force_y += radius_factor*distance_factor*a.mass * ny
            
            m = a.mass
            r = a.radius
            m = max(0.0, min(1.0, m / MAX_MASS))
            r = max(0.0, min(1.0, r / MAX_RADIUS))
            mass_factor = 1-edge_damping(m, 1.8)
            radius_factor = 1.0 - edge_damping(r, 1.8)
            speed_factor = mass_factor*radius_factor

            a.velocity[0] += total_force_x  * dt * speed_factor
            a.velocity[1] += total_force_y  * dt * speed_factor



    def update(self, dt):
        self.check_input(dt)
        self.apply_forces(dt)
        self.apply_absorption(dt)
        
        self.entities = [e for e in self.entities if e.mass > 0.1 and e.radius > 0.1]

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
    radius = 100,
    mass = 100),
]
balls+=[Ball(
    color = random.choice([Colors.RED, Colors.BLUE]),
    pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)],\
    radius = random.randint(3, 20), 
    mass = random.randint(3, 40)) for _ in range(100)]

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
        game_state.update_ai(FIXED_DT)
        camera.update(game_state.entities[0].pos,game_state.entities[0].radius)
        accumulator -= FIXED_DT

    # Отрисовка
    screen.fill(Colors.WHITE)
    draw_grid(screen,camera,screen.get_width(),screen.get_height(),20,(200,200,200))
    for ball in game_state.entities:

        screen_pos = camera.apply(ball.pos)
        mass_norm = max(0, min(1, ball.mass / MAX_MASS))
        alpha = int(MIN_ALPHA + mass_norm * (MAX_ALPHA - MIN_ALPHA))
        draw_ball_with_alpha(screen, ball.color, screen_pos, int(ball.radius * PIXELS_PER_METER*camera.zoom), alpha)

    # Обновление кадра
    pygame.display.flip() 



pygame.quit()
sys.exit()