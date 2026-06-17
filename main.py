import config
import pygame
from pygame.locals import *
import sys
import math
import random
from collections import defaultdict
pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Agar.io")

clock = pygame.time.Clock()

food_hash = defaultdict(list)
class Ball:
    def __init__(self,pos: tuple,color,mass=None):
        self.pos = pos
        self.color = color
        self.view_point=(0,0)
        self.mass=mass or config.MINIMUM_MASS
        self.is_alive = True
        self.lost_mass_to_spawn = 0

    @property
    def radius(self):
        return math.sqrt(self.mass)
    
    @property
    def speed(self):
        return math.sqrt(self.radius)/self.radius
    
    @property
    def normal(self):
        dx = self.view_point[0] - self.pos[0]
        dy = self.view_point[1] - self.pos[1]
        distance = (dx**2 + dy**2)**0.5
        if distance==0:
            return (0,0)
        return (dx/distance,dy/distance)

class Food:
    def __init__(self,pos: tuple):
        self.pos = pos
        self.mass = 1
        self.is_eaten = False
        self.color = config.COLOR_GREEN
    
    @property
    def radius(self):
        return math.sqrt(self.mass)


balls = [Ball((screen.get_width()//2, screen.get_height()//2),config.COLOR_BLUE,mass=1000 )]

foods = [Food((random.randint(0, screen.get_width()), random.randint(0,screen.get_height()))) for i in range(100)]
for food in foods:
    cell_pos = (food.pos[0]//config.CELL_SIZE,food.pos[1]//config.CELL_SIZE)

    food_hash[cell_pos].append(food)

def ai(ball:Ball):
    return (0,0)

def update(dt,foods,balls):
    
    for ball in balls:
        new_mass = config.MINIMUM_MASS + (ball.mass-config.MINIMUM_MASS)*(0.99)**dt
        ball.lost_mass_to_spawn += ball.mass-new_mass
        if ball.lost_mass_to_spawn>=config.FOOD_MASS:
            random_R = random.uniform(ball.radius+ball.radius*0.1,ball.radius+ball.radius*0.2)
            random_angle = random.uniform(0,2*math.pi)
            food_pos = (ball.pos[0]+random_R*math.cos(random_angle),ball.pos[1]+random_R*math.sin(random_angle))
            new_food = Food(food_pos)
            foods.append(new_food)
            cell_pos = (new_food.pos[0]//config.CELL_SIZE,new_food.pos[1]//config.CELL_SIZE)
            food_hash[cell_pos].append(new_food)
            ball.lost_mass_to_spawn -= config.FOOD_MASS
        ball.mass = new_mass
        x_start = int((ball.pos[0]-ball.radius)//config.CELL_SIZE)
        x_end = int((ball.pos[0]+ball.radius)//config.CELL_SIZE)
        y_start = int((ball.pos[1]-ball.radius)//config.CELL_SIZE)
        y_end = int((ball.pos[1]+ball.radius)//config.CELL_SIZE)
        for x_cell in range(x_start,x_end+1):
            for y_cell in range(y_start,y_end+1):
                for food in food_hash.get((x_cell,y_cell),[]):
                    dx = abs(food.pos[0]-ball.pos[0])
                    dy = abs(food.pos[1]-ball.pos[1])
                    dist = math.sqrt(dx**2+dy**2)
                    if dist<ball.radius:
                        if not food.is_eaten:
                            food.is_eaten=True
                            ball.mass+=1
      
 

        if ball == balls[0]:
            ball.view_point = pygame.mouse.get_pos()
        else:
            ball.view_point = ai(ball)
        normal = ball.normal
        speed = ball.speed
        new_x = ball.pos[0]+ normal[0]*speed
        new_y = ball.pos[1] + normal[1]*speed
        ball.pos = (new_x,new_y)
    foods = [food for food in foods if not food.is_eaten]
    balls = balls
    return foods,balls
    
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill((255,255,255))
    dt = clock.tick(60)/1000
    foods, balls = update(dt,foods,balls)
    for ball in balls:
        pygame.draw.circle(screen,ball.color, ball.pos,ball.radius)

    for food in foods:
        pygame.draw.circle(screen,food.color, food.pos,food.radius)

    pygame.display.flip()