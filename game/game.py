import config
import math
from collections import defaultdict
import pygame
import random
from entities import ball,food
from ai import ai
Ball = ball.Ball
Food = food.Food
print(Ball)
class Game:
    def __init__(self,time,start_mass):
        self.time = time
        self.start_time=0
        self.start_mass=start_mass
        self.blue_score=0
        self.red_score=0
        self.is_over=False

        self.balls = []
        self.foods = []
        self.food_hash = defaultdict(list)
    def start(self):
        for food in range(self.start_mass):
            blue_pos = (random.uniform(0,(config.WINDOW_WIDTH//2)*0.95),random.uniform(0,config.WINDOW_HEIGHT))
            self.create_food(blue_pos)
            red_pos = (random.uniform((config.WINDOW_WIDTH//2)*1.05,config.WINDOW_WIDTH),random.uniform(0,config.WINDOW_HEIGHT))
            self.create_food(red_pos)
        self.start_time = pygame.time.get_ticks()

    def make_balls(self,cell_pos):
        orange_food = [food for food in self.food_hash[cell_pos] if food.team==config.TEAM_RED]
        green_food = [food for food in self.food_hash[cell_pos] if food.team==config.TEAM_BLUE]
        for i in range(len(green_food)//config.MINIMUM_MASS):
            self.balls.append(Ball(pos=(cell_pos[0]*config.MINIMUM_MASS,cell_pos[1]*config.MINIMUM_MASS),
                color = config.COLOR_BLUE,
                team = config.TEAM_BLUE))
            for j in range(config.MINIMUM_MASS):
                green_food[j].is_eaten=True
                self.blue_score-=1
        for i in range(len(orange_food)//config.MINIMUM_MASS):
            self.balls.append(Ball(pos=(cell_pos[0]*config.MINIMUM_MASS,cell_pos[1]*config.MINIMUM_MASS),
                color = config.COLOR_RED,
                team = config.TEAM_RED))
            for j in range(config.MINIMUM_MASS):
                orange_food[j].is_eaten=True
                self.red_score-=1
        self.food_hash[cell_pos] = [food for food in self.food_hash[cell_pos] if not food.is_eaten]
        self.foods = [food for food in self.foods if not food.is_eaten]

    def create_food(self,pos):
        new_food = Food(pos)
        self.foods.append(new_food)
        cell_pos = (new_food.pos[0]//config.MINIMUM_MASS,new_food.pos[1]//config.MINIMUM_MASS)
        self.food_hash[cell_pos].append(new_food)
        orientation = new_food.pos[0]//(config.WINDOW_WIDTH//2)
        if orientation==config.TEAM_BLUE:
            new_food.team=config.TEAM_BLUE
            new_food.color = config.COLOR_GREEN
            self.blue_score+=new_food.mass
        elif orientation==config.TEAM_RED:
            new_food.team=config.TEAM_RED
            new_food.color = config.COLOR_ORANGE
            self.red_score+=new_food.mass
        else:
            raise TypeError
        if len(self.food_hash[cell_pos])>=5:
            self.make_balls(cell_pos)


    
    def update(self,dt):
        
        for ball in self.balls:
            new_mass = config.MINIMUM_MASS + (ball.mass-config.MINIMUM_MASS)*(0.99)**dt
            ball.lost_mass_to_spawn += ball.mass-new_mass
            if ball.lost_mass_to_spawn>=config.FOOD_MASS:
                random_R = random.uniform(ball.radius+ball.radius*0.1,ball.radius+ball.radius*0.2)
                random_angle = random.uniform(0,2*math.pi)
                pos_x = max(0,min(config.WINDOW_WIDTH,ball.pos[0]+random_R*math.cos(random_angle)))
                pos_y = max(0,min(config.WINDOW_HEIGHT,ball.pos[1]+random_R*math.sin(random_angle)))
                food_pos = (pos_x,pos_y)
                print(food_pos)
                self.create_food(food_pos)

                ball.lost_mass_to_spawn -= config.FOOD_MASS
            ball.mass = new_mass

            #food absorbtion
            x_start = int((ball.pos[0]-ball.radius)//config.MINIMUM_MASS)
            x_end = int((ball.pos[0]+ball.radius)//config.MINIMUM_MASS)
            y_start = int((ball.pos[1]-ball.radius)//config.MINIMUM_MASS)
            y_end = int((ball.pos[1]+ball.radius)//config.MINIMUM_MASS)
            for x_cell in range(x_start,x_end+1):
                for y_cell in range(y_start,y_end+1):
                    for food in self.food_hash.get((x_cell,y_cell),[]):
                        dx = abs(food.pos[0]-ball.pos[0])
                        dy = abs(food.pos[1]-ball.pos[1])
                        dist = math.sqrt(dx**2+dy**2)
                        if dist<ball.radius:
                            if not food.is_eaten:
                                food.is_eaten=True
                                ball.mass+=1
                                if food.team==config.TEAM_BLUE:
                                    self.blue_score-=1
                                elif food.team==config.TEAM_RED:
                                    self.red_score-=1
                                else:
                                    raise TypeError
        
    
            #update_ball_pos
            if ball == self.balls[0]:
                ball.view_point = pygame.mouse.get_pos()
            else:
                ball.view_point = ai.ai(ball)
            normal = ball.normal
            speed = ball.speed
            new_x = max(ball.radius,min(config.WINDOW_WIDTH-ball.radius,ball.pos[0]+ normal[0]*speed))
            new_y = max(ball.radius,min(config.WINDOW_HEIGHT-ball.radius,ball.pos[1] + normal[1]*speed))
            ball.pos = (new_x,new_y)
        self.foods = [food for food in self.foods if not food.is_eaten]
