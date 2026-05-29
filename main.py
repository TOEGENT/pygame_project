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

import config



def mobility(entity):
    raw = 1.0 / (entity.mass * (1.0 + entity.radius * 0.1))
    return max(0.5, min(1.0, raw))

def edge_damping(x,p=2.0):
    core = 4.0 *x * (1.0-x)
    return max(0.0,core)**p

def sigmoid01(x, k=10, x0=0.5):
    return 1 / (1 + math.exp(-k * (x - x0)))

def draw_grid(surface,camera,screen_width,screen_height,cell_size,color):

    offset_x,offset_y = camera.offset[0]*config.PIXELS_PER_METER*camera.zoom,camera.offset[1]*config.PIXELS_PER_METER*camera.zoom

    cell_px = cell_size * config.PIXELS_PER_METER*camera.zoom


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

        target_offset_x = target_pos[0] - (self.width / (2*config.PIXELS_PER_METER*self.zoom))
        target_offset_y = target_pos[1] - (self.height / (2*config.PIXELS_PER_METER*self.zoom))


        self.offset[0] += (target_offset_x-self.offset[0]) *0.7
        self.offset[1] += (target_offset_y - self.offset[1])*0.7

    def apply(self,target_pos):
        return [(target_pos[0] - self.offset[0])*config.PIXELS_PER_METER*self.zoom,
                (target_pos[1]-self.offset[1])*config.PIXELS_PER_METER*self.zoom]


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
        self.radius = radius 
        self.mass = mass  
        self.velocity = [0, 0]  
        self.force = [0, 0]




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
        eps = 1e-6

        visc_min = 2.0
        visc_max = 20.0

        def smoothstep(x):
            x = 0.0 if x < 0.0 else 1.0 if x > 1.0 else x
            return x * x * (3.0 - 2.0 * x)

        n = len(self.entities)

        for i in range(n):
            a = self.entities[i]
            for j in range(i + 1, n):
                b = self.entities[j]

                dx = b.pos[0] - a.pos[0]
                dy = b.pos[1] - a.pos[1]
                dist2 = dx * dx + dy * dy
                if dist2 <= eps:
                    continue

                dist = math.sqrt(dist2)
                sum_r = a.radius + b.radius
                overlap = sum_r - dist
                if overlap <= 0.0:
                    continue

                small, big = (a, b) if a.radius <= b.radius else (b, a)
                inside_depth = big.radius - (dist + small.radius)

                band = 0.15 * small.radius + eps
                inside = smoothstep((inside_depth + band) / (2.0 * band))

                if inside <= 0.0:
                    continue

                visc = visc_min + (visc_max - visc_min) * inside * inside
                relx = a.velocity[0] - b.velocity[0]
                rely = a.velocity[1] - b.velocity[1]

                fx = -visc * inside * relx
                fy = -visc * inside * rely

                a.force[0] += fx
                a.force[1] += fy
                b.force[0] -= fx
                b.force[1] -= fy
    def apply_dynamics(self, dt):
        for e in self.entities:
            inv_mass = 1/max(e.mass,0.1)

            ax = e.force[0] * inv_mass
            ay = e.force[1] * inv_mass

            e.velocity[0] += ax * dt
            e.velocity[1] += ay * dt

            e.force=[0, 0]


    def apply_boundaries(self, dt):
        w,h = config.WIDTH, config.HEIGHT

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
        damping = 0.5

        distance = math.sqrt(dx**2 + dy**2)

        nx = dx / (distance + 1e-6)
        ny = dy / (distance + 1e-6)
        if distance > 0:

            force_x = min(config.MAX_ACCELERATION, abs(nx * spring))
            force_y = min(config.MAX_ACCELERATION, abs(ny * spring))
            if dx < 0:
                force_x = -force_x
            if dy < 0:
                force_y = -force_y


            player.force[0] += force_x * mobility(player) 
            player.force[1] += force_y * mobility(player)

            player.force[0] *= damping
            player.force[1] *= damping


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
                    attraction = (b.mass / a.mass) * 0.5 
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
            
            speed_mult = (config.MAX_RADIUS / max(a.radius, 1)) * 0.5
            speed_mult = max(0.1, min(2.0, speed_mult))

            a.force[0] += total_force_x * config.ACCELERATION * speed_mult * mobility(a)
            a.force[1] += total_force_y * config.ACCELERATION * speed_mult * mobility(a)



    def update(self, dt):

        for e in self.entities:
            e.force = [0, 0]

        self.check_input(dt)
        self.update_ai(dt)
        self.apply_forces(dt)
        self.apply_absorption(dt)
        self.apply_dynamics(dt)
        self.entities = [e for e in self.entities if e.mass > 0.1 and e.radius > 0.1]

        for entity in self.entities:

            entity.velocity[0] *= (1 - config.FRICTION*dt)
            entity.velocity[1] *= (1 - config.FRICTION*dt)

            entity.pos[0] += entity.velocity[0] * dt
            entity.pos[1] += entity.velocity[1] * dt

        self.apply_boundaries(dt)
        


running=True

balls = [
    Ball(
    color = Colors.RED,
    pos = [400, 300],
    radius = 5,
    mass = 10),
]
balls+=[Ball(
    color = random.choice([Colors.RED, Colors.BLUE]),
    pos = [random.uniform(0, config.WIDTH), random.uniform(0, config.HEIGHT)],
    radius = random.randint(5,config.MAX_RADIUS), 
    mass = random.randint(5,config.MAX_MASS)) for _ in range(200)]

entities=balls
game_state = GameState(entities)

camera = Camera(screen.get_width(),screen.get_height())


while running:

    dt = clock.tick(60) / 1000.0
    ACCUMULATOR += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    while ACCUMULATOR >= config.FIXED_DT:

        
        game_state.update(config.FIXED_DT)
        camera.update(game_state.entities[0].pos,game_state.entities[0].radius)
        ACCUMULATOR -= config.FIXED_DT

    screen.fill(Colors.WHITE)
    draw_grid(screen,camera,screen.get_width(),screen.get_height(),20,(200,200,200))
    for ball in game_state.entities:

        screen_pos = camera.apply(ball.pos)
        mass_norm = max(0, min(1, ball.mass / config.MAX_MASS))
        alpha = int(config.MIN_ALPHA + mass_norm * (config.MAX_ALPHA - config.MIN_ALPHA))
        draw_ball_with_alpha(screen, ball.color, screen_pos, int(ball.radius * config.PIXELS_PER_METER*camera.zoom), alpha)

    pygame.display.flip() 



pygame.quit()
sys.exit()