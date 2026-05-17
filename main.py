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


ACCELERATION = 2
FRICTION = 0.1
FIXED_DT = 1/15
accumulator = 0
PIXELS_PER_METER = 10 
HEIGHT = 100
WIDTH = 100

MAX_MASS = 20
MIN_ALPHA = 0
MAX_ALPHA = 255
MAX_RADIUS = 20
MAX_SPEED = 100
MAX_ACCELERATION = 1000


def mobility(entity):
    raw = 1.0 / (entity.mass * (1.0 + entity.radius * 0.1))
    return max(0.5, min(1.0, raw))

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


        self.offset[0] += (target_offset_x-self.offset[0]) *0.7
        self.offset[1] += (target_offset_y - self.offset[1])*0.7

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
        k = 100000
        c = 6
        gamma = 80
        fmax = 1e5
        eps = 1e-6
        
        for i in range(len(self.entities)):
            a = self.entities[i]
            density_a = a.mass / a.radius**2
            for j in range(i+1, len(self.entities)):
                b = self.entities[j]

                dx = a.pos[0] - b.pos[0]
                dy = a.pos[1] - b.pos[1]
                dist = math.hypot(dx, dy)
                density_b = b.mass / b.radius**2

                peff= (density_a+density_b)/2
                if dist < eps:
                    continue

                overlap = (a.radius + b.radius) - dist
                if overlap <=0:
                    continue


                nx = dx / dist
                ny = dy / dist

                vrel_x = a.velocity[0] - b.velocity[0]
                vrel_y = a.velocity[1] - b.velocity[1]
                vrel_n = vrel_x * nx + vrel_y * ny

                alpha = overlap / max(min(a.radius, b.radius),eps)

                if alpha <=0.5:
                    
                    f_mag = peff * overlap - c * vrel_n 

                    f_mag = max(-fmax,min(fmax,f_mag))
                    Fx = f_mag * nx
                    Fy = f_mag * ny
                else:
                    j = -(1+0.2)*vrel_n
                    j*=peff
                    j/=(1/a.mass + 1/b.mass)
                    j = max(-fmax,min(fmax,j))
                    Jx = j * nx
                    Jy = j * ny

                    Fx = Jx
                    Fy = Jy
                

                a.velocity[0] += (Fx/a.mass) * dt
                a.velocity[1] += (Fy/a.mass) * dt 
                b.velocity[0] -= (Fx/b.mass) * dt
                b.velocity[1] -= (Fy/b.mass)  * dt
                
                



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
        dx = mouse_pos[0] - screen_center[0]
        dy = mouse_pos[1] - screen_center[1]

        spring = 1
        damping = 0.95

        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:

            force_x = min(MAX_ACCELERATION, abs(dx * spring  * dt))
            force_y = min(MAX_ACCELERATION, abs(dy * spring  * dt))
            if dx < 0:
                force_x = -force_x
            if dy < 0:
                force_y = -force_y
            player.velocity[0] += force_x
            player.velocity[1] += force_y

            player.velocity[0] *= damping
            player.velocity[1] *= damping


    def update_ai(self, dt):

        for i in range(0,len(self.entities)):
            if self.entities[i] == self.entities[0]:
                continue

            total_force_x = 0
            total_force_y = 0  
            a = self.entities[i]
            
            for j in range(0, len(self.entities)):
                b = self.entities[j]
                if a == b:
                    continue

                dx = a.pos[0] - b.pos[0]
                dy = a.pos[1] - b.pos[1]
                distance = max(0.1, math.sqrt(dx**2 + dy**2))
                
                if distance > a.radius*15 + b.radius:
                    total_force_x += random.uniform(-1, 1) * 0.3
                    total_force_y += random.uniform(-1, 1) * 0.3
                    continue
                
                nx = dx / distance
                ny = dy / distance
                
                if a.radius > b.radius:
                    attraction = (b.mass / a.mass) * 0.5  # Нормализация по массе
                    distance_influence = max(0, 1.0 - distance / (a.radius * 20))
                    force = attraction * distance_influence
                    total_force_x -= force * nx
                    total_force_y -= force * ny
                else:
                    threat = (b.mass / a.mass) * 0.7
                    distance_influence = max(0, 1.0 - distance / (a.radius * 20))
                    force = threat * distance_influence
                    total_force_x += force * nx
                    total_force_y += force * ny
            
            speed_mult = (MAX_RADIUS / max(a.radius, 1)) * 0.5
            speed_mult = max(0.1, min(2.0, speed_mult))

            a.velocity[0] += total_force_x * ACCELERATION * speed_mult * dt
            a.velocity[1] += total_force_y * ACCELERATION * speed_mult * dt



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
    radius = 10,
    mass = 1),
]
balls+=[Ball(
    color = random.choice([Colors.RED, Colors.BLUE]),
    pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)],\
    radius = random.randint(1,10), 
    mass = random.randint(1,10)) for _ in range( 10)]

entities=balls
game_state = GameState(entities)

camera = Camera(screen.get_width(),screen.get_height())


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

    screen.fill(Colors.WHITE)
    draw_grid(screen,camera,screen.get_width(),screen.get_height(),20,(200,200,200))
    for ball in game_state.entities:

        screen_pos = camera.apply(ball.pos)
        mass_norm = max(0, min(1, ball.mass / MAX_MASS))
        alpha = int(MIN_ALPHA + mass_norm * (MAX_ALPHA - MIN_ALPHA))
        draw_ball_with_alpha(screen, ball.color, screen_pos, int(ball.radius * PIXELS_PER_METER*camera.zoom), alpha)

    pygame.display.flip() 



pygame.quit()
sys.exit()