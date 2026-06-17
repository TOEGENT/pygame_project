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


class Game:
    def __init__(self,time,start_mass):
        self.time = time
        self.start_time=0
        self.start_mass=start_mass
        self.blue_score=0
        self.red_score=0
        self.is_over=False

        self.balls = [Ball((screen.get_width()//2, screen.get_height()//2),config.COLOR_BLUE,mass=1000 )]
        self.foods = []
        self.food_hash = defaultdict(list)
    def start(self):
        for food in range(self.start_mass):
            blue_pos = (random.uniform(0,(config.WINDOW_WIDTH//2)*0.95),random.uniform(0,config.WINDOW_HEIGHT))
            self.create_food(blue_pos)
            red_pos = (random.uniform((config.WINDOW_WIDTH//2)*1.05,config.WINDOW_WIDTH),random.uniform(0,config.WINDOW_HEIGHT))
            self.create_food(red_pos)
        self.start_time = pygame.time.get_ticks()

    def create_food(self,pos):
        new_food = Food(pos)
        self.foods.append(new_food)
        cell_pos = (new_food.pos[0]//config.CELL_SIZE,new_food.pos[1]//config.CELL_SIZE)
        self.food_hash[cell_pos].append(new_food)
        orientation = new_food.pos[0]//(config.WINDOW_WIDTH//2)
        if orientation==config.TEAM_BLUE:
            new_food.team=config.TEAM_BLUE
            new_food.color = config.COLOR_GREEN
            game.blue_score+=new_food.mass
        elif orientation==config.TEAM_RED:
            new_food.team=config.TEAM_RED
            new_food.color = config.COLOR_ORANGE
            game.red_score+=new_food.mass
        else:
            raise TypeError
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
        self.team = None
        self.color = None
    @property
    def radius(self):
        return math.sqrt(self.mass)
    


game = Game(10*1000,start_mass=500)




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
            game.create_food(food_pos)

            ball.lost_mass_to_spawn -= config.FOOD_MASS
        ball.mass = new_mass
        x_start = int((ball.pos[0]-ball.radius)//config.CELL_SIZE)
        x_end = int((ball.pos[0]+ball.radius)//config.CELL_SIZE)
        y_start = int((ball.pos[1]-ball.radius)//config.CELL_SIZE)
        y_end = int((ball.pos[1]+ball.radius)//config.CELL_SIZE)
        for x_cell in range(x_start,x_end+1):
            for y_cell in range(y_start,y_end+1):
                for food in game.food_hash.get((x_cell,y_cell),[]):
                    dx = abs(food.pos[0]-ball.pos[0])
                    dy = abs(food.pos[1]-ball.pos[1])
                    dist = math.sqrt(dx**2+dy**2)
                    if dist<ball.radius:
                        if not food.is_eaten:
                            food.is_eaten=True
                            ball.mass+=1
                            if food.team==config.TEAM_BLUE:
                                game.blue_score-=1
                            elif food.team==config.TEAM_RED:
                                game.red_score-=1
                            else:
                                raise TypeError
      
 

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




blue_font = pygame.font.Font(None,size=30)
red_font = pygame.font.Font(None,size=30)

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
    game.foods, game.balls = update(dt,game.foods,game.balls)
    for ball in game.balls:
        pygame.draw.circle(screen,ball.color, ball.pos,ball.radius)

    for food in game.foods:
        pygame.draw.circle(screen,food.color, food.pos,food.radius)


    pygame.display.flip()